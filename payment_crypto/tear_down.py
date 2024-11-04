import boto3
controlplane_client = boto3.client("payment-cryptography")

keys = controlplane_client.list_keys()
for key in keys['Keys']:
    if key['KeyState'] == 'CREATE_COMPLETE':
        print("Deleting %s" % key['KeyArn'])
        controlplane_client.delete_key(KeyIdentifier=key['KeyArn'])

aliases = controlplane_client.list_aliases()
print(aliases)
for alias in aliases['Aliases']:
    print("Deleting %s" % alias['AliasName'])
    controlplane_client.delete_alias(AliasName=alias['AliasName'])
