import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from backend.engine import tara_score, yoni_score, bhakoot_score, nadi_score, nadi_pada_vedha, navamsa_sign_from_longitude

def test_tara_sample():
    assert tara_score(15,25) == 3.0

def test_yoni_sample():
    # Swati = Mahisha, Purva Bhadrapada = Simha
    assert yoni_score(15,25) == 1

def test_bhakoot_sample():
    # Libra vs Aquarius = 5/9
    assert bhakoot_score(7,11) == 0

def test_nadi_sample():
    # Antya vs Adya
    assert nadi_score(15,25) == 8

def test_pada_vedha_pairs():
    assert nadi_pada_vedha(10,1,10,4)
    assert nadi_pada_vedha(10,2,10,3)
    assert not nadi_pada_vedha(10,1,10,2)
