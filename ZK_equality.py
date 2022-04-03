from zksk import Secret, DLRep
from zksk import utils

def ZK_equality(G,H):

    #Generate two El-Gamal ciphertexts (C1,C2) and (D1,D2)
    # Setup: generate a secret randomizer for the commitment scheme.
    r1 = Secret(utils.get_random_num(bits=128))
    r2 = Secret(utils.get_random_num(bits=128))
    m = Secret(utils.get_random_num(bits=128))
    r1_value = r1.value
    r2_value = r2.value
    m_value = m.value
    #Generate a NIZK proving equality of the plaintexts
    '''
    C1C2D1D2=r1∗G=r1∗H+m∗G=r2∗G=r2∗H+m∗G
    '''
    C1 = r1_value * G
    C2 = r1_value * H + m_value * G
    D1 = r2_value * G
    D2 = r2_value * H + m_value * G
    stmt = DLRep(C1,r1*G) & DLRep(C2,r1*H+m*G) & DLRep(D1,r2*G) & DLRep(D2,r2*H+m*G)
    zk_proof = stmt.prove()
    #Return two ciphertexts and the proof
    return (C1,C2), (D1,D2), zk_proof

