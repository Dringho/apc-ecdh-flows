import sys
import boto3
import time

sys.path.append('./')
from payment_crypto.ecdh.crypto_utils import CryptoUtils

private_ca = boto3.client("acm-pca")


def create_certificate_authority():
    # create Certificate Authority for short-lived certificates
    ca_arn = private_ca.create_certificate_authority(
        CertificateAuthorityConfiguration={
            'KeyAlgorithm': 'EC_prime256v1',
            'SigningAlgorithm': 'SHA256WITHECDSA',
            'Subject': {
                'CommonName': 'pindemo',
            },
        },
        CertificateAuthorityType='ROOT',
        UsageMode='SHORT_LIVED_CERTIFICATE'
    )['CertificateAuthorityArn']

    state = "CREATING"
    while state == "CREATING":
        time.sleep(1)
        state = private_ca.describe_certificate_authority(CertificateAuthorityArn=ca_arn)['CertificateAuthority'][
            'Status']
        print(state)
    return ca_arn


print("Creating AWS Private CA")
cert_authority_arn = create_certificate_authority()
print("Getting CA CSR")
csr = private_ca.get_certificate_authority_csr(CertificateAuthorityArn=cert_authority_arn)['Csr']
print("self-signing CSR")
certificate, chain = CryptoUtils.sign_with_private_ca(cert_authority_arn, csr, {
    'Value': 10,
    'Type': 'YEARS'
}, template='arn:aws:acm-pca:::template/RootCACertificate/V1')
print("Importing signed certificate as ROOT")
private_ca.import_certificate_authority_certificate(CertificateAuthorityArn=cert_authority_arn, Certificate=certificate)

print("Setup complete")
print("Please load this ENV for the rest of the demo to work")
print("export CA_ARN='%s'" % cert_authority_arn)
