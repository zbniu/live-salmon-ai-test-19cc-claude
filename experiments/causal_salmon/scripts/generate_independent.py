"""Independent finite-pool generator; never imports the main implementation.

Selftest: .venv/bin/python scripts/generate_independent.py --selftest
Final:   .venv/bin/python scripts/generate_independent.py [--resume]
Purpose 2/3 execution requires the shared freeze, framework, explicit user
authorization receipt, and both initial code registrations. No model is called.
"""
import os
for _thread_key in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_thread_key] = "1"

import argparse
from concurrent.futures import ProcessPoolExecutor
from contextlib import redirect_stdout, redirect_stderr
from datetime import datetime, timezone
import fcntl
import hashlib
import io
import json
import math
from pathlib import Path
import platform
import re
import sys
import traceback
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import numpy as np
from verification.generator import uniform, encode_csv, decode_csv, hidden_csv
from verification.materials import construct, block, replacement_table, anonymize, verify_structure, protocol_bytes
from verification.reference import run_reference
from verification.statistics import absent, coverage, difference, standardized, partitions, stratified_difference
from verification.evaluate import diagnostic_two, check_gen

PROTOCOL_HASH = "f85fedf447c734d9d5e7a2cb630284fe18c7091c5cf653610adbc43ec8e7144c"
STUDY = 20260929
WORLD = {"A": 1, "B": 2, "C": 3}
EXPECTED_PARAMETERS = dict(n=2000, a=45, b_multiplier=3, gamma=.25, beta=.5,
                           kappa=1.2, M=900, K=600, m_intercept=10, effect_fraction=.1)
FINAL_CASES = [(phase, w, s, purpose) for phase, purpose, start in
    (("development", 2, 730001), ("formal", 3, 740001)) for w in "ABC" for s in range(start, start+10)]
CONFIG = "configs/data_generation.json"
GENERATION_PROTOCOL = "docs/DATA_GENERATION_PROTOCOL.md"
GENERATION_PROTOCOL_HASH = "6b4442aeb3f4561e8254b712b8e17ca77f8605b34c85699b8dfc248ebe916e7b"
CODE_RECEIPT = "manifests/independent_code.json"
INITIAL = "manifests/generation_independent_initial.json"
MAIN_INITIAL = "manifests/generation_main_initial.json"
FRAMEWORK = "manifests/offline_framework.json"
AUTHORIZATION = "manifests/data_authorization.json"


def digest(blob):
    return hashlib.sha256(blob).hexdigest()


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2,
                       allow_nan=False) + "\n").encode("utf-8")


def load(relative):
    return json.loads((ROOT / relative).read_bytes())


def file_hash(relative):
    path = (ROOT / relative).resolve()
    if ROOT not in path.parents or not path.is_file():
        raise ValueError("Receipt path is outside repository or missing: " + relative)
    return digest(path.read_bytes())


def write_once(path, blob):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(blob)
        stream.flush()
        os.fsync(stream.fileno())


def environment():
    return dict(python=platform.python_version(), numpy=np.__version__, platform=platform.platform(),
                machine=platform.machine(), executable=str(Path(sys.executable).resolve()))


def code_files():
    paths = sorted((ROOT / "verification").glob("*.py")) + [Path(__file__).resolve()]
    return {str(p.relative_to(ROOT)): digest(p.read_bytes()) for p in paths}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate_inputs():
    require(digest(protocol_bytes(ROOT)) == PROTOCOL_HASH, "Frozen protocol mismatch")
    require(sys.version_info[:3] == (3, 12, 13) and np.__version__ == "2.5.3",
            "Locked Python3.12.13/NumPy2.5.3 required")
    selected = load("configs/selected_parameters.json")
    confirmation = load("manifests/parameter_confirmation.json")
    require(selected["status"] == "confirmed" and selected["candidate"] == "K1"
            and selected["parameters"] == EXPECTED_PARAMETERS, "Confirmed K1 complete row required")
    require(selected["protocol_sha256"] == PROTOCOL_HASH
            and confirmation["protocol_sha256"] == PROTOCOL_HASH
            and confirmation["confirmed_candidate"] == "K1"
            and confirmation["confirmed_complete_row"] == EXPECTED_PARAMETERS
            and confirmation["selected_configuration_sha256"] == file_hash("configs/selected_parameters.json")
            and confirmation["calibration_report_sha256"] == selected["calibration_report_sha256"],
            "Parameter confirmation provenance mismatch")
    seeds = load("configs/seeds.json")
    require(seeds["study_tag"] == STUDY and seeds["world_codes"] == WORLD
            and seeds["bootstrap_count"] == 200, "Seed registration mismatch")
    require(seeds["purposes"]["selftest"]["code"] == 4
            and seeds["purposes"]["selftest"]["initial_test_seeds"] == [709000,709009],
            "Selftest registration mismatch")
    return selected["parameters"], (ROOT / "planning.md").read_text()


def expected_materials(protocol, params):
    require(verify_structure(protocol), "World assignment paragraph structure mismatch")
    materials = {}
    for world in "ABC":
        for version, blob in construct(protocol, world, params["n"], params["M"], params["K"]).items():
            materials[f"materials/{version}/{world}.md"] = blob
    materials["materials/prompt.txt"] = block(protocol, "prompt").encode()
    materials["materials/substitutions.json"] = json_bytes({"replacements": replacement_table(protocol)})
    allowed_numbers = {0,1,2,3,4,5,6,100,params["n"],params["M"],params["K"]}
    forbidden = re.compile(r"SATT|Gumbel|World\s+[ABC]|u_i|m_i|10%|0\.10|703\d{3}|710001|72000[123]", re.I)
    for name, blob in materials.items():
        if name.endswith(".json"):
            continue
        text = blob.decode()
        require("{{" not in text and not forbidden.search(text), "Public material leakage: " + name)
        require(all(float(n) in allowed_numbers for n in re.findall(r"\d+(?:\.\d+)?", text)),
                "Unexpected number in public material: " + name)
    require(not re.search(r"causal|identif|confound|adjust|random", materials["materials/prompt.txt"].decode(), re.I),
            "Non-neutral prompt")
    return materials


def verify_registration(relative):
    initial = load(relative)
    require(initial["passed"] is True and bool(initial["files"]), "Both initial selftests required")
    for name, pinned in initial["files"].items():
        # Only compute byte fingerprints; never import or inspect main code.
        require(file_hash(name) == pinned, "Initial code fingerprint changed: " + name)
    for key in ("python", "numpy", "platform"):
        require(initial["environment"][key] == environment()[key], "Initial environment mismatch: " + key)
    return initial


def validate_gates(params, protocol, require_initials=True):
    frozen = load('configs/frozen_study.json')
    freeze = load('manifests/freeze.json')
    require(frozen['parameters'] == params and frozen['protocol_sha256'] == PROTOCOL_HASH, 'Frozen parameters differ')
    expected = expected_materials(protocol, params)
    require(set(expected) == set(frozen['materials']), 'Material set differs')
    for name, blob in expected.items():
        actual = (ROOT / name).read_bytes()
        same = json.loads(actual) == json.loads(blob) if name.endswith('.json') else actual == blob
        require(same and digest(actual) == frozen['materials'][name], 'Material identity differs: ' + name)
    require(freeze['configuration_sha256'] == file_hash('configs/frozen_study.json'), 'Freeze identity differs')
    framework = load(FRAMEWORK)
    for name, pinned in framework['files'].items():
        require(file_hash(name) == pinned, 'Framework evidence differs: ' + name)
    require(all(framework['checks'][k] for k in ('ACC-5-reference','ACC-7-reference')), 'Isolation checks incomplete')
    config = load(CONFIG)
    authorization = load(AUTHORIZATION)
    require(file_hash(GENERATION_PROTOCOL) == GENERATION_PROTOCOL_HASH and
            authorization['config_sha256'] == file_hash(CONFIG) and
            authorization['generation_protocol_sha256'] == GENERATION_PROTOCOL_HASH and
            authorization['model_calls_authorized'] is False, 'Generation authorization differs')
    require(config['parameters'] == params and config['study_tag'] == STUDY and
            config['worlds'] == list('ABC') and config['pool_count'] == 60 and
            config['selected_count'] == 12 and config['pool_extension_allowed'] is False and
            config['qualify_all_applicable_GEN'] is True and
            config['selection'] == 'first_qualifying_seeds_in_ascending_order_per_phase_world', 'Pool specification differs')
    require(config['phases'] == {
        'development': dict(purpose=2, seeds=list(range(730001,730011)), quota_per_world=1),
        'formal': dict(purpose=3, seeds=list(range(740001,740011)), quota_per_world=3)}, 'Registered matrix differs')
    gates = dict(freeze=freeze, framework=framework, authorization=authorization, config=config)
    if require_initials:
        gates['main_initial'] = verify_registration(MAIN_INITIAL)
        gates['independent_initial'] = verify_registration(INITIAL)
        require(gates['independent_initial']['files'] == code_files(), 'Independent registration incomplete')
        require(gates['independent_initial']['config_sha256'] == file_hash(CONFIG), 'Independent config differs')
    return gates

def generate(params, world, seed, purpose):
    require(world in WORLD and ((purpose == 4 and 709000 <= seed <= 709009)
            or (purpose == 2 and 730001 <= seed <= 730010) or (purpose == 3 and 740001 <= seed <= 740010)),
            "Unregistered final/selftest purpose or seed")
    n, K, M = params["n"], params["K"], params["M"]
    streams, draws = {}, {}
    def draw(variable):
        entropy = [STUDY,purpose,seed,WORLD[world],variable]
        streams[str(variable)] = entropy
        draws[variable] = uniform(entropy, n)
        return draws[variable]
    root3 = math.sqrt(3.0)
    a, b = float(params["a"]), params["b_multiplier"] * root3
    y = a + 30 * draw(1)
    u = root3 * (2 * draw(2) - 1)
    epsilon = b * (2 * draw(3) - 1)
    mu = a + 15
    m = 10 + params["gamma"] * (y - mu) + 2 * u
    z0 = m + epsilon
    z1 = z0 + .1 * m
    rows = np.arange(n)
    x = np.zeros(n, dtype=np.int64)
    hidden = dict(row=rows,y=y,u=u,epsilon=epsilon,m=m,z0=z0,z1=z1)
    if world == "A":
        lottery = draw(4)
        chosen = np.lexsort((rows,lottery))[:K]
    else:
        G = -np.log(-np.log(draw(5)))
        base = (params["beta"] * (y - mu)) / 15
        w = base + G if world == "B" else (base + params["kappa"] * u) + G
        application_tie, admission_tie = draw(6), draw(7)
        applicants = np.lexsort((rows,-application_tie,-w))[:M]
        chosen = applicants[np.lexsort((applicants,-admission_tie[applicants],-y[applicants]))[:K]]
        flag = np.zeros(n, dtype=np.int64)
        flag[applicants] = 1
        hidden.update(G=G,w=w,applicant=flag)
    x[chosen] = 1
    hidden["admitted"] = x
    observed = np.where(x == 1,z1,z0)
    public = encode_csv(x,y,observed)
    xp,yp,zp = decode_csv(public)
    T = float(.1 * np.mean(m[x == 1]))
    lower = 10 - 15 * params["gamma"] - 2 * root3
    upper = 10 + 15 * params["gamma"] + 2 * root3
    invariants = dict(
        analytic_bounds=bool(lower > 0 and a+lower-b >= 0 and a+30+1.1*upper+b <= 100),
        individual_effects=bool(np.all(m>0) and np.all(z1-z0>0) and np.max(np.abs(z1-z0-.1*m)) <= 1e-9),
        potential_bounds=bool(np.all((y+z0>=0)&(y+z0<=100)&(y+z1>=0)&(y+z1<=100))),
        csv_roundtrip=bool(np.array_equal(x,xp) and np.array_equal(y.view(np.uint64),yp.view(np.uint64)) and np.array_equal(observed.view(np.uint64),zp.view(np.uint64))),
        outcome_recomputed=bool(np.array_equal(m,10+params["gamma"]*(y-mu)+2*u) and np.array_equal(z0,m+epsilon) and np.array_equal(z1,z0+.1*m)),
        counts=bool(int(x.sum())==K and (world=="A" or int(hidden["applicant"].sum())==M)),
        valid_csv=bool(len(xp)==n and np.all(np.isfinite(yp)) and np.all(np.isfinite(zp)) and np.all((yp+zp>=0)&(yp+zp<=100))))
    truth = dict(T=T,SATT=T,parameters=params,world=world,seed=seed,purpose=purpose,
                 streams=streams,bootstrap_streams=[[STUDY,purpose,seed,WORLD[world],20,b] for b in range(200)] if world=="B" else [],
                 csv_sha256=digest(public),participants=int(x.sum()),
                 applicants=None if world=="A" else int(hidden["applicant"].sum()),
                 leakage_probe="SALMON_FINAL_INDEPENDENT_PRIVATE_"+uuid.uuid4().hex)
    return public,(xp,yp,zp),hidden,truth,invariants


def compute(params,world,seed,purpose,protocol):
    public,projection,hidden,truth,invariants = generate(params,world,seed,purpose)
    x,y,z = projection
    T = truth["T"]
    raw = difference(x,z)
    detail = {}
    if world=="A":
        primary,bins = raw,None
    else:
        primary,detail = standardized(x,y,z)
        bins,_ = partitions(x,y)
    primary = coverage(primary,T)
    bootstrap = []
    if world=="B":
        d1,_ = stratified_difference(x,y,z)
        d2,bootstrap,d2detail = diagnostic_two(x,y,z,seed,purpose,world,params["a"]+15)
        detail["D2_point"] = d2detail
        d1,d2 = coverage(d1,T),coverage(d2,T)
    else:
        d1 = absent("world_not_B","not_applicable")
        d2 = dict(**absent("world_not_B","not_applicable"),max_weight=None,ess=None,bootstrap_successes=0,bootstrap_failures=[])
    descriptions = construct(protocol,world,len(x),params["M"],params["K"])
    refs = {v:run_reference(public,blob) for v,blob in descriptions.items()}
    pairing = anonymize(descriptions["named"].decode(),replacement_table(protocol)).encode()==descriptions["anonymized"]
    for version,ref in refs.items():
        require(ref["input_hashes"] == {"data.csv":digest(public),"STUDY_DESCRIPTION.md":digest(descriptions[version])}, "Reference input hash mismatch")
        require(truth["leakage_probe"] not in json.dumps(ref), "Hidden leakage probe exposed")
    record = dict(candidate="K1",world=world,seed=seed,purpose=purpose,csv_sha256=truth["csv_sha256"],
        x=x.tolist(),n=len(x),participants=int(x.sum()),applicants=truth["applicants"],T=T,
        identity_error=float(abs(np.mean((hidden["z1"]-hidden["z0"])[x==1])-.1*np.mean(hidden["m"][x==1]))),
        N=raw["E"],primary=primary,D1=d1,D2=d2,bins=bins,invariants=invariants,
        GEN=check_gen(world,invariants,primary,T,raw["E"],bins,refs,pairing),
        reference={v:{k:r[k] for k in ("input_hashes","method","correct","format_valid","input_boundary_passed","numeric")} for v,r in refs.items()},details=detail,
        ACC={"ACC-2":all(invariants[k] for k in ("valid_csv","csv_roundtrip")),"ACC-3":pairing,"ACC-6-probe-created":True})
    return record,public,hidden,truth,bootstrap,descriptions,refs


def verify_complete(folder):
    if not (folder/"COMPLETE").exists():
        return False
    evidence = (folder/"evidence.sha256.json").read_bytes()
    require((folder/"COMPLETE").read_text().strip()==digest(evidence), "COMPLETE digest mismatch")
    manifest = json.loads(evidence)
    actual = {str(p.relative_to(folder)) for p in folder.rglob("*") if p.is_file()} - {"COMPLETE","evidence.sha256.json"}
    require(actual == set(manifest["files"]), "Completed file inventory changed")
    for name, pinned in manifest["files"].items():
        require(digest((folder/name).read_bytes())==pinned, "Completed evidence changed: "+name)
    return True


def save_case(folder,computed):
    record,public,hidden,truth,bootstrap,descriptions,refs = computed
    if folder.exists():
        require(not verify_complete(folder), "Complete case cannot be overwritten")
        folder.rename(folder.with_name(".retained-incomplete-"+folder.name+"-"+uuid.uuid4().hex))
    temp = folder.with_name(".partial-"+folder.name+"-"+uuid.uuid4().hex)
    temp.mkdir(parents=True)
    write_once(temp/"data.csv",public)
    write_once(temp/"students.csv",hidden_csv(hidden))
    saved = np.genfromtxt(io.BytesIO((temp/"students.csv").read_bytes()),delimiter=",",names=True,dtype=np.float64)
    for name,array in hidden.items():
        require(np.array_equal(saved[name].astype(np.float64).view(np.uint64),array.astype(np.float64).view(np.uint64)), "Hidden CSV roundtrip: "+name)
    for array,expected in ((saved["m"],10+truth["parameters"]["gamma"]*(saved["y"]-(truth["parameters"]["a"]+15))+2*saved["u"]),
                           (saved["z0"],saved["m"]+saved["epsilon"]),(saved["z1"],saved["z0"]+.1*saved["m"])):
        require(np.array_equal(array.view(np.uint64),expected.view(np.uint64)), "Saved hidden outcome recomputation failed")
    for name,value in (("truth.json",truth),("record.json",record),("bootstrap.json",bootstrap)):
        write_once(temp/name,json_bytes(value))
    for version,ref in refs.items():
        target = temp/version
        write_once(target/"data.csv",public)
        write_once(target/"STUDY_DESCRIPTION.md",descriptions[version])
        write_once(target/"reference.json",json_bytes(ref))
        write_once(target/"report.md",ref["report"].encode())
        write_once(target/"input_manifest.json",json_bytes(ref["input_hashes"]))
        write_once(target/"access_audit.json",json_bytes({k:ref[k] for k in ("access_log","probes","sandbox_profile","executable_sha256","statistics_sha256")}))
    require((temp/"named/data.csv").read_bytes()==(temp/"anonymized/data.csv").read_bytes()==public,"Paired CSV mismatch")
    files = {str(p.relative_to(temp)):digest(p.read_bytes()) for p in sorted(temp.rglob("*")) if p.is_file()}
    evidence = json_bytes(dict(files=files))
    write_once(temp/"evidence.sha256.json",evidence)
    write_once(temp/"COMPLETE",(digest(evidence)+"\n").encode())
    temp.rename(folder)
    for p in folder.rglob("*"):
        if p.is_file():
            p.chmod(0o444)
    require(verify_complete(folder), "Saved case verification failed")



def register_code():
    receipt = dict(schema_version=1, implementation="independent", phase="data_source_registration",
                   files=code_files(), environment=environment(), model_calls=0,
                   input_hashes={p:file_hash(p) for p in (CONFIG, GENERATION_PROTOCOL, AUTHORIZATION, "planning.md")})
    path = ROOT/CODE_RECEIPT
    if path.exists():
        require(load(CODE_RECEIPT) == receipt, "Registered source changed; preserve invalidated version and repeat all selftests")
    else:
        write_once(path,json_bytes(receipt))
        path.chmod(0o444)
    return receipt


def run_identity(selftest, gates):
    names = ["planning.md", GENERATION_PROTOCOL, CONFIG, "docs/VERIFICATION_CONTRACT.md",
             "configs/selected_parameters.json", "configs/seeds.json", "configs/frozen_study.json",
             "manifests/parameter_confirmation.json", "manifests/freeze.json",
             FRAMEWORK, AUTHORIZATION, "uv.lock", "pyproject.toml", CODE_RECEIPT]
    if not selftest:
        names += [MAIN_INITIAL, INITIAL]
    return dict(implementation="independent",selftest=selftest,code=code_files(),environment=environment(),
                inputs={p:file_hash(p) for p in names},fixed_cases=FINAL_CASES if not selftest else
                [("selftest",w,s,4) for w in "ABC" for s in range(709000,709010)],model_calls=0)


def worker(job):
    base, phase, world, seed, purpose, params, protocol, selftest = job
    base = Path(base)
    folder = base/phase/f"{world}-{seed}"
    if verify_complete(folder):
        return str(folder)
    try:
        computed = compute(params,world,seed,purpose,protocol)
        if selftest:
            from verification.generator import generate as original_selftest_generate
            original = original_selftest_generate(dict(params,id="K1"),world,seed,4)
            require(computed[1] == original[0], "Selftest generator CSV differs from frozen independent generator")
            for name,array in computed[2].items():
                require(np.array_equal(array,original[2][name]), "Selftest hidden generator mismatch: " + name)
        save_case(folder,computed)
        return str(folder)
    except Exception as error:
        failure = base/"failed_attempts"/(f"{world}-{seed}-"+uuid.uuid4().hex)
        path = failure/"failure.json"
        write_once(path,json_bytes(dict(world=world,seed=seed,purpose=purpose,exception=repr(error),
                   traceback=traceback.format_exc(),classification="implementation_error_pending_review")))
        path.chmod(0o444)
        raise


def register_initial(base, records, summary):
    require(len(records)==30 and all(r["purpose"]==4 for r in records), "Complete purpose-4 selftest required")
    require(all(all(r["invariants"].values()) and r["identity_error"]<=1e-9 and
                r["primary"]["status"]=="ok" and all(ref["correct"] and ref["format_valid"] and
                ref["input_boundary_passed"] for ref in r["reference"].values()) for r in records),
            "Selftest invariant/reference/primary failed")
    b_records = [r for r in records if r["world"]=="B"]
    require(len(b_records)==10 and all(r["D1"]["status"]==r["D2"]["status"]=="ok" and
            r["D2"]["bootstrap_successes"]==200 and not r["D2"]["bootstrap_failures"] for r in b_records),
            "Selftest complete B diagnostic workload failed")
    evidence = {str(p.relative_to(ROOT)):digest(p.read_bytes()) for p in sorted(base.rglob("*"))
                if p.is_file() and ((p.name == "COMPLETE" and "selftest" in p.relative_to(base).parts) or p.name in ("selftest_run_identity.json","selftest_summary.json","focused_checks.json"))}
    initial = dict(schema_version=1,implementation="independent",phase="data_initial_selftest",
        passed=True,environment=environment(),files=code_files(),evidence=evidence,model_calls=0,
        config_sha256=file_hash(CONFIG),
        fixed_data_generated=False,candidate_pool_generated=False,
        independence=dict(imports_main=False,read_main_entry=False,read_main_numerical_results=False,
                          read_main_tests=False,read_src=False),
        selftest=dict(command=".venv/bin/python scripts/generate_independent.py --selftest",
            purpose=4,seeds=[709000,709009],worlds=list("ABC"),records=30,public_references=60,
            B_bootstrap_attempts=2000,original_independent_generator_csv_and_hidden_bitwise_equal=True,
            focused_tests=6,resume_verified=True,quality_failures_preserved=summary["failures"]))
    path = ROOT/INITIAL
    if path.exists():
        require(load(INITIAL)==initial,"Immutable initial registration mismatch")
    else:
        write_once(path,json_bytes(initial))
        path.chmod(0o444)


def focused_checks(params, base):
    rejected = []
    for world, seed, purpose in (("A",710001,2),("A",720001,3),("A",730001,3),
                                 ("B",740001,2),("C",730011,2),("C",740011,3)):
        try:
            generate(params,world,seed,purpose)
        except ValueError:
            rejected.append([world,seed,purpose])
        else:
            raise ValueError("Purpose/seed guard accepted unregistered combination")
    result = dict(passed=True,checks=6,rejected_purpose_seed_pairs=rejected,
                  candidate_seed_generation_performed=False)
    path = base/"focused_checks.json"
    blob = json_bytes(result)
    if path.exists():
        require(path.read_bytes()==blob,"Focused checks changed")
    else:
        write_once(path,blob)
        path.chmod(0o444)


def execute(args, params, protocol, gates, base):
    identity = run_identity(args.selftest,gates)
    identity_path = base/("selftest_run_identity.json" if args.selftest else "run_identity.json")
    if identity_path.exists():
        require(args.resume,"Existing immutable run; use --resume")
        require(json.loads(identity_path.read_bytes())==json.loads(json_bytes(identity)),
                "Immutable identity mismatch; preserve existing run")
    else:
        require(not args.resume,"No existing run to resume")
        write_once(identity_path,json_bytes(identity))
        identity_path.chmod(0o444)
    # The selftest and pool live under one implementation directory but have independent identities.
    if args.selftest:
        focused_checks(params,base)
    cases = identity["fixed_cases"]
    jobs = [(str(base),phase,w,s,p,params,protocol,args.selftest) for phase,w,s,p in cases]
    records=[]
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        for case, result in zip(cases, executor.map(worker,jobs)):
            phase,world,seed,purpose = case
            folder=Path(result)
            require(verify_complete(folder),"Worker evidence verification failed")
            record=json.loads((folder/"record.json").read_bytes())
            require((record["world"],record["seed"],record["purpose"])==(world,seed,purpose),"Case identity mismatch")
            records.append(record)
            print(json.dumps(dict(completed=len(records),phase=phase,world=world,seed=seed,
                GEN={k:v["passed"] for k,v in record["GEN"].items()})),flush=True)
            numerical_failure = record["primary"]["status"]!="ok" or (world=="B" and
                                (record["D1"]["status"]!="ok" or record["D2"]["status"]!="ok"))
            require(not numerical_failure,"Numerical failure retained; halt pending independent investigation")
    probes=[json.loads((base/phase/f"{w}-{s}"/"truth.json").read_bytes())["leakage_probe"] for phase,w,s,_ in cases]
    require(len(set(probes))==len(probes),"Hidden leakage probes must be unique")
    failures=[dict(world=r["world"],seed=r["seed"],GEN={k:v["reasons"] for k,v in r["GEN"].items()
              if v["applicable"] and not v["passed"]}) for r in records
              if any(v["applicable"] and not v["passed"] for v in r["GEN"].values())]
    qualifying_counts, selected_cases = {}, []
    selection_complete = False
    if not args.selftest:
        selection_complete = True
        for phase in ("development","formal"):
            quota = gates["config"]["phases"][phase]["quota_per_world"]
            purpose = gates["config"]["phases"][phase]["purpose"]
            for world in "ABC":
                qualifying = sorted((r for r in records if r["world"]==world and r["purpose"]==purpose
                              and all(v["passed"] for v in r["GEN"].values() if v["applicable"])),
                              key=lambda r:r["seed"])
                qualifying_counts[phase+"/"+world] = len(qualifying)
                selection_complete = selection_complete and len(qualifying)>=quota
                selected_cases += [dict(phase=phase,world=world,seed=r["seed"]) for r in qualifying[:quota]]
    summary=dict(records=len(records),selftest=args.selftest,purpose=4 if args.selftest else None,
                 implementation_checks_passed=True,all_GEN_passed=not failures,batch_eligible=False,
                 eligibility_reason="selftest_only" if args.selftest else "Screening and independent comparison deferred",
                 failures=failures,model_calls=0,code=code_files(),environment=environment(),
                 scope="selftest_only" if args.selftest else "independent_candidate_pool",
                 qualifying_counts=qualifying_counts,selected_cases=selected_cases,
                 selection_complete=selection_complete,
                 selection_scope="not_applicable_selftest" if args.selftest else "local_GEN_pending_independent_comparison")
    path=base/("selftest_summary.json" if args.selftest else "summary.json")
    blob=json_bytes(summary)
    if path.exists():
        require(path.read_bytes()==blob,"Immutable summary changed")
    else:
        write_once(path,blob)
        path.chmod(0o444)
    if args.selftest:
        # Exercise all complete-case and immutable fingerprint checks before attesting resume.
        require(json.loads(identity_path.read_bytes())==json.loads(json_bytes(run_identity(True,gates))),
                "Selftest resume identity verification failed")
        require(all(verify_complete(base/phase/f"{w}-{s}") for phase,w,s,_ in cases),"Selftest resume seal verification failed")
        register_initial(base,records,summary)
    print(json.dumps(dict(records=len(records),summary_sha256=digest(blob),all_GEN_passed=not failures,
                         selftest=args.selftest,model_calls=0)),flush=True)


def main(argv=None):
    parser=argparse.ArgumentParser()
    parser.add_argument("--selftest",action="store_true")
    parser.add_argument("--resume",action="store_true")
    parser.add_argument("--workers",type=int,default=2)
    parser.add_argument("--check-preconditions",action="store_true")
    args=parser.parse_args(argv)
    require(args.workers in (1,2),"Only one or two single-thread numerical workers allowed")
    params,protocol=validate_inputs()
    gates=validate_gates(params,protocol,require_initials=not args.selftest)
    register_code()
    if args.check_preconditions:
        print(json.dumps(dict(preconditions_passed=True,selftest=args.selftest,model_calls=0)))
        return
    base=ROOT/"results/quality_checks/data/independent"
    base.mkdir(parents=True,exist_ok=True)
    with (base/".run.lock").open("a+b") as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        log_path=base/"logs"/(datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")+"-"+
                   ("selftest" if args.selftest else "pool")+("-resume" if args.resume else "")+"-"+uuid.uuid4().hex+".log")
        log_path.parent.mkdir(parents=True,exist_ok=True)
        try:
            with log_path.open("x",encoding="utf-8") as log:
                with redirect_stdout(log),redirect_stderr(log):
                    try:
                        execute(args,params,protocol,gates,base)
                    except Exception:
                        traceback.print_exc()
                        raise
        finally:
            log_path.chmod(0o444)
        print(json.dumps(dict(log=str(log_path.relative_to(ROOT)),completed=True,selftest=args.selftest)))


if __name__ == "__main__":
    main()
