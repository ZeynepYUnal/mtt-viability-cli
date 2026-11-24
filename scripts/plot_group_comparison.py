import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

# Sentetik çoklu grup canlılık verisi (n=4 tekrar)
np.random.seed(42)
groups = ['Control\n(DMSO)', 'Drug A\n(10 µM)', 'Drug B\n(10 µM)', 'Combo\n(A + B)']
data = [
    np.random.normal(100.0, 3.5, 4),
    np.random.normal(76.5, 4.2, 4),
    np.random.normal(64.0, 3.8, 4),
    np.random.normal(34.2, 3.1, 4)
]

means = [np.mean(d) for d in data]
sds = [np.std(d, ddof=1) for d in data]
colors = ['#7F8C8D', '#5DADE2', '#2E86C1', '#1B4F72']

fig, ax = plt.subplots(figsize=(6.5, 5), dpi=300)

# Bar ve hata çubukları
x = np.arange(len(groups))
bars = ax.bar(x, means, yerr=sds, capsize=5, width=0.55, color=colors,
              edgecolor='black', linewidth=1, error_kw={'elinewidth': 1.2, 'ecolor': 'black'}, zorder=2)

# Bireysel deney noktaları (replicate overlay)
for i, d in enumerate(data):
    jitter = np.random.uniform(-0.08, 0.08, size=len(d))
    ax.scatter(np.repeat(x[i], len(d)) + jitter, d, color='white', edgecolor='black',
               s=35, zorder=3, linewidth=1)

# İstatistiksel anlamlılık çizgileri (Kontrole karşı t-testi)
def add_stat_bracket(ax, x1, x2, y, h, text):
    ax.plot([x1, x1, x2, x2], [y, y+h, y+h, y], lw=1.2, c='black')
    ax.text((x1 + x2) * 0.5, y + h + 1, text, ha='center', va='bottom', color='black', fontsize=11, fontweight='bold')

p_vals = [stats.ttest_ind(data[0], data[i]).pvalue for i in range(1, 4)]
labels = ['***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else 'ns' for p in p_vals]

add_stat_bracket(ax, 0, 1, 108, 2.5, labels[0])
add_stat_bracket(ax, 0, 2, 118, 2.5, labels[1])
add_stat_bracket(ax, 0, 3, 128, 2.5, labels[2])

ax.set_ylabel('Cell Viability (% of Control)', fontsize=11, fontweight='bold')
ax.set_title('Comparative Cytotoxicity & Combination Treatment Analysis', fontsize=12, fontweight='bold', pad=15)
ax.set_xticks(x)
ax.set_xticklabels(groups, fontsize=10, fontweight='bold')
ax.set_ylim(0, 142)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.yaxis.grid(True, linestyle='--', alpha=0.4, zorder=1)

plt.tight_layout()
plt.savefig('results/group_comparison_portfolio.png', dpi=300)
print("Portfolio figure saved to: results/group_comparison_portfolio.png")
