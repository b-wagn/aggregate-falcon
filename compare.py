import argparse
import proof_size_estimate

"""
Size Comparison for Blockchain Transactions
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
parser.add_argument(
    "--plot",
    action="store_true",
    help="Plot comparison graph for N from 0 to 10,000"
)

args = parser.parse_args()
N = args.num_transactions


def aggregated_signature_size(N):
    """
    Aggregated signature size a_N.
    Does not yet count the salts.
    """

    proof_size_bits = proof_size_estimate.search(N, 15, proof_size_estimate.FALCON_64_128(), proof_size_estimate.CHAL_2_SPLIT_64_128(),8, False)
    return proof_size_bits / 8






# =========================
# Size Calculations
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

print("Size Comparison (in bytes)")
print("-" * 40)

print(f"Number of transactions (N): {N}")
print()
print()

print("Case 1: With Key Recovery, No Aggregation")
print(f"  Total size: {case1_total:,} bytes")
print()

print("Case 2: Without Key Recovery, No Aggregation")
print(f"  Total size: {case2_total:,} bytes")
print()

print("Case 3: Without Key Recovery, With Aggregation")
print(f"  Aggregated signature size a_N: {a_N:,} bytes")
print(f"  Total size: {case3_total:,} bytes")
print()

# =========================
# Plotting
# =========================

if args.plot:
    import matplotlib.pyplot as plt
    import numpy as np

    # Range of N values - start from 64 as smaller values may fail
    N_values = np.linspace(64, 1000, 50, dtype=int)
    N_values = np.unique(N_values)  # Remove duplicates

    case1_values = []
    case2_values = []
    case3_values = []
    valid_N_values = []

    print("Calculating storage costs for plotting...")
    for i, n in enumerate(N_values):
        try:
            # Case 3: Without Key Recovery, With Aggregation (calculate first as it may fail)
            a_n = aggregated_signature_size(n)
            c3 = n * p + a_n + n * r

            # Case 1: With Key Recovery, No Aggregation
            c1 = n * (h + s_tilde + r)

            # Case 2: Without Key Recovery, No Aggregation
            c2 = n * (p + s + r)

            case1_values.append(c1)
            case2_values.append(c2)
            case3_values.append(c3)
            valid_N_values.append(n)

            if (i + 1) % 10 == 0:
                print(f"  Progress: {i + 1}/{len(N_values)}")
        except Exception as e:
            print(f"  Skipping N={n}: {e}")

    # Convert to KB 
    case1_kb = np.array(case1_values) / 1024
    case2_kb = np.array(case2_values) / 1024
    case3_kb = np.array(case3_values) / 1024
    valid_N_values = np.array(valid_N_values)

    # Find intersection point between Case 1 and Case 3
    diff = case1_kb - case3_kb
    # Find where the sign changes (crossing point)
    sign_changes = np.where(np.diff(np.sign(diff)))[0]
    if len(sign_changes) > 0:
        idx = sign_changes[0]
        # Linear interpolation to find exact intersection
        x1, x2 = valid_N_values[idx], valid_N_values[idx + 1]
        y1_diff, y2_diff = diff[idx], diff[idx + 1]
        intersection_x = x1 - y1_diff * (x2 - x1) / (y2_diff - y1_diff)
        print(f"\nIntersection point (Case 1 & Case 3): N = {intersection_x:.0f}")
    else:
        intersection_x = None

    colors = ['#2E86AB', '#A23B72', '#F18F01']  # Blue, Magenta, Orange

    plt.figure(figsize=(10, 6))
    plt.plot(valid_N_values, case1_kb, label='Case 1: Key Recovery, No Aggregation', linewidth=2, color=colors[0])
    plt.plot(valid_N_values, case2_kb, label='Case 2: No Key Recovery, No Aggregation', linewidth=2, color=colors[1])
    plt.plot(valid_N_values, case3_kb, label='Case 3: No Key Recovery, With Aggregation', linewidth=2, color=colors[2])

    if intersection_x is not None:
        plt.axvline(x=intersection_x, color='gray', linestyle='--', linewidth=1.5, alpha=0.7)

    plt.xlabel('Number of Signatures (N)', fontsize=12)
    plt.ylabel('Size (KB)', fontsize=12)
    plt.title('Size Comparison for Falcon Signatures', fontsize=14)
    plt.legend(loc='upper left', fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    plt.savefig('storage_comparison.png', dpi=150)
    print(f"\nPlot saved to storage_comparison.png")
