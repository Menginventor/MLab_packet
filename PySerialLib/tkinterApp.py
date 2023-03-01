import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation

# Create a Tkinter window
root = tk.Tk()
root.title("Real-Time Plot")

# Create a Matplotlib figure
fig = plt.Figure()

# Add a subplot to the figure
ax = fig.add_subplot(1, 1, 1)

# Create a list to store the data
data = []


# Define the update function
def update(frame):
    # Clear the plot
    ax.clear()

    # Add the new data point
    data.append(frame)

    # Plot the data
    ax.plot(data)

    # Set the axis labels
    ax.set_xlabel("Time")
    ax.set_ylabel("Value")

    # Adjust the plot limits
    ax.set_xlim(0, len(data))
    ax.set_ylim(min(data), max(data))

    # Redraw the plot
    canvas.draw()


# Create a Tkinter canvas
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

# Create an animation
ani = FuncAnimation(fig, update, frames=range(100), interval=50)

# Start the Tkinter event loop
root.mainloop()
