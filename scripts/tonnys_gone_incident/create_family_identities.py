#!/usr/bin/env python3
"""Create Identity objects for the DeLorenzo family."""

from letta_client import Letta

# Family member data from the memory blocks
FAMILY_MEMBERS = [
    {
        "identifier_key": "jarad_delorenzo",
        "name": "Jarad DeLorenzo",
        "label": "Dad",
        "identity_type": "user",
        "metadata": {
            "role": "father",
            "occupation": "Software Architect & Futurist",
            "relationship": "Tonny's best friend since 2004",
            "age_group": "adult",
            "interests": ["technology", "AI", "software development", "33GOD pipeline"]
        }
    },
    {
        "identifier_key": "carrie_delorenzo",
        "name": "Carrie DeLorenzo",
        "label": "Mom",
        "identity_type": "user",
        "metadata": {
            "role": "mother",
            "relationship": "Jarad's wife (married 10 years)",
            "age_group": "adult",
            "notes": "Tonny playfully teases her in good fun"
        }
    },
    {
        "identifier_key": "ava_delorenzo",
        "name": "Ava DeLorenzo",
        "label": "Ava",
        "identity_type": "user",
        "metadata": {
            "role": "daughter",
            "age": 10,
            "gender": "female",
            "grade": "5th",
            "age_group": "child"
        }
    },
    {
        "identifier_key": "chase_delorenzo",
        "name": "Chase DeLorenzo",
        "label": "Chase",
        "identity_type": "user",
        "metadata": {
            "role": "son",
            "age": 8,
            "gender": "male",
            "grade": "3rd",
            "age_group": "child"
        }
    },
    {
        "identifier_key": "dominic_delorenzo",
        "name": "Dominic DeLorenzo",
        "label": "Dominic",
        "identity_type": "user",
        "metadata": {
            "role": "son",
            "age": 4,
            "gender": "male",
            "grade": "preschool",
            "age_group": "child"
        }
    }
]

def create_family_identities():
    """Create Identity objects for each DeLorenzo family member."""
    client = Letta(base_url="http://localhost:8283")

    print("="*80)
    print("CREATING DELORENZO FAMILY IDENTITIES")
    print("="*80)

    created_identities = []

    for member in FAMILY_MEMBERS:
        print(f"\n👤 Creating identity for {member['name']}...")

        try:
            # Create the identity with basic required parameters only
            identity = client.identities.create(
                identifier_key=member["identifier_key"],
                name=member["name"],
                identity_type=member["identity_type"]
            )

            # Note: metadata stored in member dict for reference but not passed to API

            print(f"   ✓ Created: {identity.name} (ID: {identity.id})")
            created_identities.append(identity)

        except Exception as e:
            print(f"   ✗ Error: {e}")

    print("\n" + "="*80)
    print(f"✓ Created {len(created_identities)} identities")
    print("="*80)

    # List all identities to verify
    print("\nAll identities in system:")
    identities = client.identities.list()
    for identity in identities:
        print(f"  - {identity.name} (ID: {identity.id})")

    return created_identities

if __name__ == "__main__":
    create_family_identities()
