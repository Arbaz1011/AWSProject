import boto3

# Initialize a Cognito client
cognito_client = boto3.client('cognito-idp', region_name='us-east-1')

# Global variables to store IDs
USER_POOL_ID = None
CLIENT_ID = None

def create_user_pool(pool_name):
    global USER_POOL_ID  # Add global declaration
    try:
        # List existing user pools
        response = cognito_client.list_user_pools(MaxResults=60)
        for pool in response['UserPools']:
            if pool['Name'] == pool_name:
                print(f"User pool {pool_name} already exists")
                USER_POOL_ID = pool['Id']  # Store in global variable
                return pool['Id']

        # Create new pool if it doesn't exist
        response = cognito_client.create_user_pool(
            PoolName=pool_name,
            Policies={
                'PasswordPolicy': {
                    'MinimumLength': 8,
                    'RequireUppercase': True,
                    'RequireLowercase': True,
                    'RequireNumbers': True,
                    'RequireSymbols': True
                }
            },
            AutoVerifiedAttributes=['email'],
            MfaConfiguration='OFF',
        )
        USER_POOL_ID = response['UserPool']['Id']  # Store in global variable
        return USER_POOL_ID
    except Exception as e:
        print(f"Error creating/getting user pool: {str(e)}")
        return None

def create_app_client(user_pool_id):
    global CLIENT_ID  # Add global declaration
    try:
        # List existing clients
        response = cognito_client.list_user_pool_clients(
            UserPoolId=user_pool_id,
            MaxResults=60
        )
        
        for client in response['UserPoolClients']:
            if client['ClientName'] == 'car-app-client':
                print("App client already exists")
                CLIENT_ID = client['ClientId']  # Store in global variable
                return CLIENT_ID

        # Create new client if it doesn't exist
        response = cognito_client.create_user_pool_client(
            UserPoolId=user_pool_id,
            ClientName='car-app-client',
            GenerateSecret=False,
            ExplicitAuthFlows=[
                'ALLOW_USER_PASSWORD_AUTH',
                'ALLOW_REFRESH_TOKEN_AUTH',
            ],
        )
        CLIENT_ID = response['UserPoolClient']['ClientId']  # Store in global variable
        return CLIENT_ID
    except Exception as e:
        print(f"Error creating/getting app client: {str(e)}")
        return None

def get_user_pool_id():
    return USER_POOL_ID

def get_client_id():
    return CLIENT_ID

# Initialize the values when the module is imported
pool_id = create_user_pool('CarServiceUserPool')
if pool_id:  # Check if pool_id is valid
    app_client_id = create_app_client(pool_id)
    print("User Pool ID:", USER_POOL_ID)
    print("App Client ID:", CLIENT_ID)
else:
    print("Failed to create user pool, app client will not be created.")
