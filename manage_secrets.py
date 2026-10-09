import boto3
import pandas as pd
from botocore.exceptions import ClientError

# =====================================================
# Configuration
# =====================================================
REGION = "us-west-2"                      # Change to your AWS Region
EXCEL_FILE = "secrets.xlsx"       # Path to your Excel file
OUTPUT_CSV = "secret_arns.csv"            # Output file

# Create Secrets Manager client
client = boto3.client("secretsmanager", region_name=REGION)

# Store ARNs
arns = []


def create_secret(secret_name, description, secret_value):
    """
    Creates a secret in AWS Secrets Manager.
    If the secret already exists, retrieves its ARN.
    """

    arn = None

    try:
        response = client.create_secret(
            Name=secret_name,
            Description="" if pd.isna(description) else str(description),
            SecretString=str(secret_value)
        )

        arn = response["ARN"]
        print(f"✅ Created: {secret_name}")

    except client.exceptions.ResourceExistsException:
        response = client.describe_secret(SecretId=secret_name)
        arn = response["ARN"]
        print(f"⚠️ Already Exists: {secret_name}")

    except ClientError as e:
        print(f"❌ Failed to create: {secret_name} - {e.response['Error']['Message']}")
        return None

    # Save ARN
    arns.append({"ARN": arn})
    return arn


def remove_secret(secret_name):
    """
    Deletes a secret from AWS Secrets Manager.
    Uses ForceDeleteWithoutRecovery to immediately remove the secret.
    """

    try:
        client.delete_secret(
            SecretId=secret_name,
            ForceDeleteWithoutRecovery=True
        )
        print(f"🗑️ Removed: {secret_name}")
        return True

    except client.exceptions.ResourceNotFoundException:
        print(f"⚠️ Not Found (already removed): {secret_name}")
        return True

    except ClientError as e:
        print(f"❌ Failed to remove: {secret_name} - {e.response['Error']['Message']}")
        return False


def main():
    df = pd.read_excel(EXCEL_FILE)

    required_columns = [
        "Secret Name",
        "Description",
        "Secret Value (Plain Text)"
    ]

    missing = [col for col in required_columns if col not in df.columns]

    if missing:
        print(f"Missing columns: {missing}")
        return

    # Check for Status and Action columns
    has_status = "Status" in df.columns
    has_action = "Action" in df.columns

    if not has_action:
        print("⚠️ 'Action' column not found. Defaulting all rows to 'Add'.")

    added_count = 0
    removed_count = 0
    skipped_count = 0

    for idx, row in df.iterrows():

        secret_name = row["Secret Name"]

        if pd.isna(secret_name) or str(secret_name).strip() == "":
            continue

        # Check Status column - skip rows already marked as "Completed"
        if has_status:
            status = row.get("Status", "")
            if not pd.isna(status) and str(status).strip().lower() == "completed":
                skipped_count += 1
                continue

        # Determine action (default to "Add" if column missing or value empty)
        action = "Add"
        if has_action:
            raw_action = row.get("Action", "")
            if not pd.isna(raw_action) and str(raw_action).strip() != "":
                action = str(raw_action).strip()

        secret_name = str(secret_name).strip()

        if action.lower() == "add":
            description = row["Description"]
            secret_value = row["Secret Value (Plain Text)"]

            if pd.isna(secret_value):
                print(f"⏭️ Skipping (no secret value): {secret_name}")
                continue

            result = create_secret(secret_name, description, str(secret_value))
            if result:
                added_count += 1
                # Update Status to Completed in DataFrame
                if has_status:
                    df.at[idx, "Status"] = "Completed"

        elif action.lower() == "remove":
            success = remove_secret(secret_name)
            if success:
                removed_count += 1
                # Update Status to Completed in DataFrame
                if has_status:
                    df.at[idx, "Status"] = "Completed"

        else:
            print(f"⚠️ Unknown action '{action}' for: {secret_name}")

    # Write only ARNs
    pd.DataFrame(arns).to_csv(OUTPUT_CSV, index=False)

    # Save updated Excel with Status changes
    df.to_excel(EXCEL_FILE, index=False)

    print(f"\n{'='*50}")
    print(f"Summary:")
    print(f"  Added:   {added_count}")
    print(f"  Removed: {removed_count}")
    print(f"  Skipped: {skipped_count} (already completed)")
    print(f"  ARNs saved to: {OUTPUT_CSV}")
    print(f"  Excel updated with status: {EXCEL_FILE}")


if __name__ == "__main__":
    main()