import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.lines import Line2D
from sklearn.svm import SVC

# Load and transform data
df = pd.read_csv("SVG_Shape_Features.csv")
df['cx'] = df['cx'] - 50
df['cy'] = 980 - df['cy'] + 50

# Separate by class
rects = df[df['label'] == 'rectangle']
circles = df[df['label'] == 'circle']
max_samples = min(len(rects), len(circles))

# Setup figure
plt.ion()
fig, ax = plt.subplots(figsize=(8, 6), facecolor='white')

def train_and_plot(n_per_class):
    ax.clear()
    ax.set_facecolor('white')

    # Select samples
    samples = pd.concat([rects.head(n_per_class), circles.head(n_per_class)])
    X_train = samples[['cx', 'cy']].values
    y_train = samples['label'].map({'rectangle': -1, 'circle': 1}).values
    labels = samples['label'].values

    # Train SVM with RBF kernel
    clf = SVC(kernel='rbf', C=1, gamma='scale')  # You can set gamma manually like gamma=0.001
    clf.fit(X_train, y_train)

    # Compute decision surface
    xx, yy = np.meshgrid(np.linspace(0, 1820, 500),
                         np.linspace(0, 980, 500))
    Z = clf.decision_function(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)

    # Draw contours
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

    # Margin violators
    margin = y_train * clf.decision_function(X_train)
    violators = margin < 1
    ax.scatter(X_train[violators, 0], X_train[violators, 1],
               s=140, facecolors='none', edgecolors='orange',
               linewidths=2, label='Margin Violators')

    # Title and labels
    ax.set_xlim(0, 1820)
    ax.set_ylim(0, 980)
    ax.set_xlabel('Eje X')
    ax.set_ylabel('Eje Y')
    ax.set_title(f'RBF Kernel (gamma="scale") with {n_per_class} samples per class')
    ax.grid(True)

    # Legend
    legend_elements = [
        Line2D([0], [0], color='purple', lw=2, label='Decision Boundary'),
        Line2D([0], [0], color='gray', lw=1, linestyle='--', label='Margins'),
        Line2D([0], [0], marker='o', color='w', label='Support Vectors',
               markerfacecolor='none', markeredgecolor='black', markersize=10),
        Line2D([0], [0], marker='o', color='w', label='Margin Violators',
               markerfacecolor='none', markeredgecolor='orange', markersize=10)
    ]
    ax.legend(handles=legend_elements)

    plt.draw()
    plt.pause(0.8)

# Loop
for n in range(2, max_samples + 1):
    train_and_plot(n)

plt.ioff()
plt.show()
