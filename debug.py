import matplotlib.pyplot as plt
import numpy as np



def random_sinusoid(x):
    # Generate 5 random sinusoids
    result = np.zeros_like(x)
    
    for _ in range(5):
        amplitude = np.random.uniform(0.5, 3.0)  # Random amplitude between 0.5 and 3
        frequency = np.random.uniform(0.1, 2.0)   # Random frequency/speed
        phase = np.random.uniform(0, 2 * np.pi)   # Random phase
        result += amplitude * np.sin(frequency * x + phase)
    
    return result

# Generate x values
x = np.linspace(0, 10 * np.pi, 1000)

# Generate the composite sinusoid
y = random_sinusoid(x)

max_curve = np.max(y)
idx_max = np.argmax(y)
x_max = x[idx_max]

min_curve = np.min(y)
idx_min = np.argmin(y)
x_min = x[idx_min]

# Plot the result
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(x, y)
ax.set_title('Random Composite Sinusoid')
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.grid(True)

# ligne du max (depuis x_max jusqu'à la fin de l'axe x)
ax.hlines(
    y=max_curve,
    xmin=x_max,
    xmax=x[-1],
    color='r',
    linestyles='--',
    label='Max'
)

# texte affichant la valeur du max au-dessus de la ligne
dy = (y.max() - y.min()) or 1.0
offset = 0.02 * dy
# position du texte à l'extrémité droite de la ligne (légèrement en retrait)
dx = x[-1] - x[0]
x_text = x[-1] - 0.01 * dx
ax.text(
    x_text,
    max_curve + offset,
    f"{max_curve:.3f}",
    color='r',
    va='bottom',
    ha='right'
)
low, high = ax.get_ylim()
ax.set_ylim(low, max(high, max_curve + 3 * offset))

# ligne du min (depuis x_min jusqu'à la fin de l'axe x)
ax.hlines(
    y=min_curve,
    xmin=x_min,
    xmax=x[-1],
    color='b',
    linestyles='--',
    label='Min'
)

ax.legend()

plt.show()