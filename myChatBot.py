# Import openai library
import openai

# Import tkinter module
import tkinter as tk

# Set your API key
openai.api_key = "Your API key here"

# Set your model name
model = "gpt-3.5-turbo"

# Define a function to chat with the model
def chat():
    # Get user input from entry box
    user_input = e.get()
    
    # Check if user wants to quit
    if user_input.lower() == "quit":
        # Destroy the window and exit
        root.destroy()
        return
    
    # Add user message to messages list
    messages.append({"role": "user", "content": user_input})
    
    # Call chat completion endpoint with messages list as input
    response = openai.ChatCompletion.create(model=model, messages=messages)
    
    # Get assistant message from response choices
    assistant_message = response["choices"][0]["message"]["content"]
    
    # Display user and assistant messages in text area
    txt.insert(tk.END, "\nYou: " + user_input)
    txt.insert(tk.END, "\nAssistant: " + assistant_message)
    
    # Add assistant message to messages list
    messages.append({"role": "assistant", "content": assistant_message})
    
    # Clear entry box for next input
    e.delete(0, tk.END)

# Create a window object with title and size
root = tk.Tk()
root.title("My GPT Chatbot")
root.geometry("800x600")

# Initialize an empty list of messages
messages = []

# Create a text area widget for displaying messages 
txt = tk.Text(root)
txt.pack(expand=True, fill=tk.BOTH)

# Create an entry box widget for typing user input 
e = tk.Entry(root)
e.pack(side=tk.BOTTOM)

# Create a button widget for submitting user input 
b1 = tk.Button(root, text="Send", command=chat)
b1.pack(side=tk.RIGHT)

# Create another button widget for quitting application 
b2 = tk.Button(root, text="Quit", command=root.destroy)
b2.pack(side=tk.LEFT)

# Start main loop of window 
root.mainloop()