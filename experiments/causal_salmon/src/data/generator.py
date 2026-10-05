"""Protocol appendix A, without NumPy distribution sampling functions."""
import csv
import io
import math

import numpy as np

TAG = 20260929
WORLD_CODES = {'A': 1, 'B': 2, 'C': 3}


def uniform_from_raw(raw):
    return ((np.asarray(raw, dtype=np.uint64) >> np.uint64(12)).astype(np.float64) + .5) * 2.0**-52


def uniform(entropy, count):
    return uniform_from_raw(np.random.PCG64(np.random.SeedSequence(entropy)).random_raw(count))


def ranked(primary, tie):
    return np.lexsort((np.arange(len(primary)), -np.asarray(tie), -np.asarray(primary)))


def validate_seed(seed, purpose):
    if not ((purpose == 1 and 703000 <= seed <= 703999) or
            (purpose == 4 and 709000 <= seed <= 709999)):
        raise ValueError('Offline pre-confirmation generation permits only registered calibration/selftest seeds')


def generate(p, world, seed, purpose=1):
    validate_seed(seed, purpose)
    n, K, M = 2000, p['K'], p['M']
    if not (0 < K < M < n and K >= 100 and K % 5 == 0):
        raise ValueError('Invalid frozen candidate counts')
    entropies = {}
    def stream(v):
        entropy = [TAG, purpose, seed, WORLD_CODES[world], v]
        entropies[str(v)] = entropy
        return uniform(entropy, n)
    y = p['a'] + 30 * stream(1)
    u = math.sqrt(3.0) * (2 * stream(2) - 1)
    eps = p['b_multiplier'] * math.sqrt(3.0) * (2 * stream(3) - 1)
    mu = p['a'] + 15
    m = 10 + p['gamma'] * (y - mu) + 2 * u
    z0 = m + eps
    z1 = z0 + .1 * m
    x = np.zeros(n, dtype=np.int64)
    out = dict(y=y, u=u, epsilon=eps, m=m, z0=z0, z1=z1, x=x, entropy=entropies)
    if world == 'A':
        lottery = stream(4)
        x[np.lexsort((np.arange(n), lottery))[:K]] = 1
    else:
        G = -np.log(-np.log(stream(5)))
        application_tie, admission_tie = stream(6), stream(7)
        w = (p['beta'] * (y - mu)) / 15
        if world == 'C':
            w = w + p['kappa'] * u
        w = w + G
        applicant = np.zeros(n, dtype=np.int64)
        ids = ranked(w, application_tie)[:M]
        applicant[ids] = 1
        order = np.lexsort((ids, -admission_tie[ids], -y[ids]))
        x[ids[order[:K]]] = 1
        out.update(G=G, w=w, applicant=applicant, admitted=x.copy())
    out['z'] = np.where(x == 1, z1, z0)
    out['T'] = float(.1 * np.mean(m[x == 1]))
    return out


def decimal(value):
    return '0' if value == 0 else format(float(value), '.17g')


def csv_bytes(x, y, z):
    return ('x,y,z\n' + ''.join(f'{int(a)},{decimal(b)},{decimal(c)}\n' for a, b, c in zip(x, y, z, strict=True))).encode('utf-8')


def parse_csv(blob):
    text = blob.decode('utf-8')
    if not text.startswith('x,y,z\n') or not text.endswith('\n') or '\r' in text or '\ufeff' in text:
        raise ValueError('CSV encoding/header/newline violation')
    rows = list(csv.reader(io.StringIO(text)))[1:]
    if any(len(r) != 3 or r[0] not in ('0', '1') for r in rows):
        raise ValueError('CSV columns/x violation')
    x = np.array([int(r[0]) for r in rows], dtype=np.int64)
    y = np.array([float(r[1]) for r in rows], dtype=np.float64)
    z = np.array([float(r[2]) for r in rows], dtype=np.float64)
    if not np.isfinite(y).all() or not np.isfinite(z).all() or csv_bytes(x, y, z) != blob:
        raise ValueError('CSV finite .17g representation violation')
    return x, y, z


def bit_equal(a, b):
    return np.array_equal(np.asarray(a).view(np.uint64), np.asarray(b).view(np.uint64))


def check_hidden(d, p):
    mmin = 10 - 15 * p['gamma'] - 2 * math.sqrt(3.0)
    b = p['b_multiplier'] * math.sqrt(3.0)
    analytic = mmin > 0 and p['a'] + mmin - b >= 0 and p['a'] + 30 + 1.1 * (10 + 15*p['gamma'] + 2*math.sqrt(3.0)) + b <= 100
    effect = d['z1'] - d['z0']
    m = 10 + p['gamma'] * (d['y'] - (p['a'] + 15)) + 2 * d['u']
    z0, z1 = m + d['epsilon'], (m + d['epsilon']) + .1*m
    xp, yp, zp = parse_csv(csv_bytes(d['x'], d['y'], d['z']))
    bounds = np.all((d['y']+d['z0'] >= 0) & (d['y']+d['z0'] <= 100) & (d['y']+d['z1'] >= 0) & (d['y']+d['z1'] <= 100))
    return {
        'analytic_bounds': bool(analytic),
        'individual_effects': bool(np.all(d['m'] > 0) and np.all(effect > 0) and np.all(np.abs(effect - .1*d['m']) <= 1e-9)),
        'potential_bounds': bool(bounds),
        'csv_roundtrip': bool(np.array_equal(xp,d['x']) and bit_equal(yp,d['y']) and bit_equal(zp,d['z'])),
        'outcome_recomputed': bool(bit_equal(m,d['m']) and bit_equal(z0,d['z0']) and bit_equal(z1,d['z1'])),
        'counts': bool(d['x'].sum() == p['K'] and ('applicant' not in d or d['applicant'].sum() == p['M'])),
        'valid_csv': bool(len(xp) == 2000 and np.all((yp+zp >= 0) & (yp+zp <= 100))),
    }
