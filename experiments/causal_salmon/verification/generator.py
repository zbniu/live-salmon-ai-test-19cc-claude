"""Independent PCG64 raw-bit generator, exact protocol arithmetic and CSV."""
import hashlib
import io
import math
import numpy as np

STUDY = 20260929
WORLD = {"A": 1, "B": 2, "C": 3}


def uniform(entropy, count):
    raw = np.random.PCG64(np.random.SeedSequence(entropy)).random_raw(count)
    return ((raw >> 12).astype(np.float64)+0.5)*2.**-52


def descending(primary, tie, indices):
    return indices[np.lexsort((indices, -tie[indices], -primary[indices]))]


def generate(candidate, world, seed, purpose):
    if not ((purpose == 1 and 703000 <= seed <= 703999) or (purpose == 4 and 709000 <= seed <= 709999)):
        raise ValueError("Only registered calibration/selftest seeds permitted")
    n, root3 = 2000, math.sqrt(3.)
    streams = {}
    def draw(v):
        entropy = [STUDY, purpose, seed, WORLD[world], v]
        streams[str(v)] = entropy
        return uniform(entropy, n)
    a, b = float(candidate["a"]), candidate["b_multiplier"]*root3
    y = a+30*draw(1)
    u = root3*(2*draw(2)-1)
    epsilon = b*(2*draw(3)-1)
    mu = a+15
    m = 10+candidate["gamma"]*(y-mu)+2*u
    z0 = m+epsilon
    z1 = z0+0.1*m
    rows = np.arange(n)
    x = np.zeros(n, dtype=np.int64)
    hidden = dict(row=rows, y=y, u=u, epsilon=epsilon, m=m, z0=z0, z1=z1)
    if world == "A":
        lottery = draw(4)
        chosen = np.lexsort((rows, lottery))[:candidate["K"]]
    else:
        G = -np.log(-np.log(draw(5)))
        base = candidate["beta"]*(y-mu)/15
        w = base+G if world == "B" else (base+candidate["kappa"]*u)+G
        app_tie, admission_tie = draw(6), draw(7)
        applicants = descending(w, app_tie, rows)[:candidate["M"]]
        flag = np.zeros(n, dtype=np.int64)
        flag[applicants] = 1
        chosen = descending(y, admission_tie, applicants)[:candidate["K"]]
        hidden.update(G=G, w=w, applicant=flag)
    x[chosen] = 1
    hidden["admitted"] = x
    z = np.where(x == 1, z1, z0)
    public = encode_csv(x, y, z)
    xp, yp, zp = decode_csv(public)
    T = float(.1*np.mean(m[x == 1]))
    lower = 10-15*candidate["gamma"]-2*root3
    upper = 10+15*candidate["gamma"]+2*root3
    invariants = dict(analytic_bounds=bool(lower > 0 and a+lower-b >= 0 and a+30+1.1*upper+b <= 100), individual_effects=bool(np.all(m > 0) and np.all(z1-z0 > 0) and np.max(np.abs(z1-z0-.1*m)) <= 1e-9), potential_bounds=bool(np.all((y+z0 >= 0)&(y+z0 <= 100)&(y+z1 >= 0)&(y+z1 <= 100))), csv_roundtrip=bool(np.array_equal(x,xp) and np.array_equal(y.view(np.uint64),yp.view(np.uint64)) and np.array_equal(z.view(np.uint64),zp.view(np.uint64))), outcome_recomputed=bool(np.array_equal(m,10+candidate["gamma"]*(y-mu)+2*u) and np.array_equal(z0,m+epsilon) and np.array_equal(z1,z0+.1*m)), counts=bool(sum(x)==candidate["K"] and (world=="A" or sum(hidden["applicant"])==candidate["M"])), valid_csv=bool(len(xp)==n and np.all(np.isfinite(yp)) and np.all(np.isfinite(zp)) and np.all((yp+zp >= 0)&(yp+zp <= 100))))
    truth = dict(T=T, parameters=candidate, world=world, seed=seed, purpose=purpose, streams=streams, csv_sha256=hashlib.sha256(public).hexdigest(), participants=int(sum(x)), applicants=None if world=="A" else int(sum(hidden["applicant"])))
    return public, (xp, yp, zp), hidden, truth, invariants


def number(v):
    return "0" if v == 0 else format(float(v), ".17g")


def encode_csv(x, y, z):
    return ("x,y,z\n"+"".join(f"{int(a)},{number(b)},{number(c)}\n" for a,b,c in zip(x,y,z))).encode()


def decode_csv(data):
    text = data.decode("utf-8")
    if not text.startswith("x,y,z\n") or not text.endswith("\n") or "\r" in text or '"' in text:
        raise ValueError("Invalid public CSV layout")
    values = []
    for line in text.splitlines()[1:]:
        parts = line.split(",")
        if len(parts) != 3 or parts[0] not in ("0", "1") or any(p.strip()!=p for p in parts):
            raise ValueError("Invalid public CSV row")
        values.append([int(parts[0]), float(parts[1]), float(parts[2])])
    arr = np.asarray(values, dtype=np.float64)
    if not np.all(np.isfinite(arr)):
        raise ValueError("Nonfinite CSV")
    return arr[:,0].astype(np.int64), arr[:,1], arr[:,2]


def hidden_csv(hidden):
    keys = list(hidden)
    integer = {"row", "applicant", "admitted"}
    rows = [",".join(keys)]
    for i in range(len(hidden["row"])):
        rows.append(",".join(str(int(hidden[k][i])) if k in integer else number(hidden[k][i]) for k in keys))
    return ("\n".join(rows)+"\n").encode()
