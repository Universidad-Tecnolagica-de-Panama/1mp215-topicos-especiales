import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.lines import Line2D
from matplotlib.widgets import Slider
from sklearn.svm import SVC

# Load and transform data
df = pd.read_csv("SVG_Shape_Features.csv")
df['cx'] = df['cx'] - 50
df['cy'] = 980 - df['cy'] + 50

# Prepare data
rects = df[df['label'] == 'rectangle']
circles = df[df['label'] == 'circle']
samples = pd.concat([rects, circles])
X_train = samples[['cx', 'cy']].values
y_train = samples['label'].map({'rectangle': -1, 'circle': 1}).values
labels = samples['label'].values

# Create plot
fig, ax = plt.subplots(figsize=(8, 6))
plt.subplots_adjust(bottom=0.2)
ax.set_facecolor('white')

# Slider for gamma
ax_slider = plt.axes([0.25, 0.05, 0.5, 0.03])
slider = Slider(ax_slider, 'Gamma', valmin=1e-6, valmax=0.0001, valinit=0.000001, valfmt='%.6f')

# Update plot function
def update(val):
    gamma = slider.val
    ax.clear()
    ax.set_facecolor('white')

    # Train SVM with RBF kernel
    clf = SVC(kernel='rbf', C=1, gamma=gamma)
    clf.fit(X_train, y_train)

    # Decision function
    xx, yy = np.meshgrid(np.linspace(0, 1820, 500),
                         np.linspace(0, 980, 500))
    Z = clf.decision_function(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)

    # Contours: decision boundary and margins
    ax.contourf(xx, yy, Z > 0, alpha=0.1, colors=['blue', 'red'])
    ax.contour(xx, yy, Z, levels=[0], colors='purple', linewidths=2)
    ax.contour(xx, yy, Z, levels=[-1, 1], colors='gray', linestyles='--')

    # Draw shapes
    for i, (x, y) in enumerate(X_train):
        if labels[i] == 'rectangle':
            ax.add_patch(patches.Rectangle((x - 20, y - 20), 40, 40,
                                           linewidth=1, edgecolor='blue',
                                           facecolor='blue', alpha=0.7))
        else:
            ax.add_patch(patches.Circle((x, y), 20,
                                        linewidth=1, edgecolor='red',
                                        facecolor='red', alpha=0.7))

    # Support vectors
    sv = clf.support_vectors_
    ax.scatter(sv[:, 0], sv[:, 1], s=120, facecolors='none',
               edgecolors='black', linewidths=2, label='Support Vectors')

    # Labels and legend
    ax.set_xlim(0, 1820)
    ax.set_ylim(0, 980)
    ax.set_xlabel('Eje X')
    ax.set_ylabel('Eje Y')
    ax.set_title(f'RBF Kernel with Variable Gamma')
    ax.grid(True)

    legend_elements = [
        Line2D([0], [0], color='purple', lw=2, label='Decision Boundary'),
        Line2D([0], [0], color='gray', lw=1, linestyle='--', label='Margins'),
        Line2D([0], [0], marker='o', color='w', label='Support Vectors',
               markerfacecolor='none', markeredgecolor='black', markersize=10)
    ]
    ax.legend(handles=legend_elements)

    fig.canvas.draw_idle()

# Initial draw and connect slider
update(None)
slider.on_changed(update)

plt.show()
