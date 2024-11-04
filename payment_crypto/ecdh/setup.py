import base64
import boto3

KEY_ALIAS_PREFIX = "pindemo-"
controlplane_client = boto3.client("payment-cryptography")
private_ca = boto3.client("acm-pca")


def apc_trust_ca_certificate(certificate_authority):
    key_arn = controlplane_client.import_key(Enabled=True, KeyMaterial={
        'RootCertificatePublicKey': {
            'KeyAttributes': {
                'KeyAlgorithm': 'ECC_NIST_P256',
                'KeyClass': 'PUBLIC_KEY',
                'KeyModesOfUse': {
                    'Verify': True,
                },
                'KeyUsage': 'TR31_S0_ASYMMETRIC_KEY_FOR_DIGITAL_SIGNATURE',
            },
            'PublicKeyCertificate': base64.b64encode(certificate_authority.encode('UTF-8')).decode('UTF-8')
        }
    }, KeyCheckValueAlgorithm='ANSI_X9_24', Tags=[])['Key']['KeyArn']

    return key_arn


def get_key_by_alias(alias):
    alias = "alias/%s%s" % (KEY_ALIAS_PREFIX, alias)
    try:
        answer = controlplane_client.get_alias(AliasName=alias)
        return answer["Alias"]["KeyArn"]
    except:
        return None


def create_alias(alias, key_arn):
    alias = "alias/%s%s" % (KEY_ALIAS_PREFIX, alias)
    controlplane_client.create_alias(AliasName=alias, KeyArn=key_arn)


def apc_generate_pgk():
    alias = "pgk"
    key_arn = get_key_by_alias(alias)
    if key_arn is None:
        key_arn = controlplane_client.create_key(Exportable=True,
                                                 KeyAttributes={
                                                     "KeyAlgorithm": "TDES_2KEY",
                                                     "KeyUsage": "TR31_V2_VISA_PIN_VERIFICATION_KEY",
                                                     "KeyClass": "SYMMETRIC_KEY",
                                                     "KeyModesOfUse": {"Generate": True, "Verify": True}
                                                 })['Key']['KeyArn']
        create_alias(alias, key_arn)
    return key_arn


def apc_generate_pek():
    alias = "pek"
    key_arn = get_key_by_alias(alias)
    if key_arn is None:
        key_arn = controlplane_client.create_key(Exportable=True,
                                                 KeyAttributes={
                                                     "KeyAlgorithm": "TDES_3KEY",
                                                     "KeyUsage": "TR31_P0_PIN_ENCRYPTION_KEY",
                                                     "KeyClass": "SYMMETRIC_KEY",
                                                     "KeyModesOfUse": {"Encrypt": True, "Decrypt": True, "Wrap": True,
                                                                       "Unwrap": True}
                                                 })['Key']['KeyArn']
        create_alias(alias, key_arn)
    return key_arn


def apc_generate_ecdh():
    alias = "ecdh"
    key_arn = get_key_by_alias(alias)
    if key_arn is None:
        key_arn = controlplane_client.create_key(Enabled=True, Exportable=True, KeyAttributes={
            'KeyAlgorithm': 'ECC_NIST_P256',
            'KeyClass': 'ASYMMETRIC_KEY_PAIR',
            'KeyModesOfUse': {
                'DeriveKey': True
            },
            'KeyUsage': 'TR31_K3_ASYMMETRIC_KEY_FOR_KEY_AGREEMENT'
        })['Key']['KeyArn']
        create_alias(alias, key_arn)
    return key_arn


def setup(ca_arn):
    private_ca = boto3.client("acm-pca")
    ca_certificate = private_ca.get_certificate_authority_certificate(CertificateAuthorityArn=ca_arn)['Certificate']
    ca_key_arn = apc_trust_ca_certificate(ca_certificate)
    pgk_arn = apc_generate_pgk()
    pek_arn = apc_generate_pek()
    ecdh_arn = apc_generate_ecdh()

    return ca_key_arn, pgk_arn, pek_arn, ecdh_arn

