import argparse
import proof_size_estimate

"""
Storage Cost Comparison for Blockchain Transactions
using Falcon Signatures
"""

# =========================
# Parameters (in bytes)
# =========================

# Signature sizes
s = 666-40     # signature size when public key is known
s_tilde = 2*s  # signature size when only hash of public key is known
r = 40         # nonce size

# Key / address sizes
p = 897        # public key size
h = 160/8      # address size (hash of public key)

# Number of transactions
parser = argparse.ArgumentParser(description="Storage cost estimation")
parser.add_argument(
    "-N", "--num-transactions",
    type=int,
    default=1024,
    help="Number of transactions (default: 1024)"
)

args = parser.parse_args()
N = args.num_transactions

# Aggregated signature size function
# You can modify this to match your aggregation scheme
def aggregated_signature_size(N):
    """
    Aggregated signature size a_N.
    Does not yet count the salts.
    """

    proof_size_bits = proof_size_estimate.search(N, 15, proof_size_estimate.FALCON_64_128(), proof_size_estimate.CHAL_2_SPLIT_64_128(),8, False)
    return proof_size_bits / 8






# =========================
# Storage Cost Calculations
# =========================

# Case 1: With Key Recovery, No Aggregation
case1_total = N * (h + s_tilde + r)

# Case 2: Without Key Recovery, No Aggregation
case2_total = N * (p + s + r)

# Case 3: Without Key Recovery, With Aggregation
# Note: a_N already counts the salts
a_N = aggregated_signature_size(N)
case3_total = N * p + a_N + N * r



# =========================
# Output
# =========================

print("Storage Cost Comparison (in bytes)")
print("-" * 40)

print(f"Number of transactions (N): {N}")
print()
print()

print("Case 1: With Key Recovery, No Aggregation")
print(f"  Total storage: {case1_total:,} bytes")
print()

print("Case 2: Without Key Recovery, No Aggregation")
print(f"  Total storage: {case2_total:,} bytes")
print()

print("Case 3: Without Key Recovery, With Aggregation")
print(f"  Aggregated signature size a_N: {a_N:,} bytes")
print(f"  Total storage: {case3_total:,} bytes")
print()