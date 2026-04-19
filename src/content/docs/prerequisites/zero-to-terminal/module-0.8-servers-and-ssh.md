---
title: "Module 0.8: Servers and SSH"
slug: prerequisites/zero-to-terminal/module-0.8-servers-and-ssh
sidebar:
  order: 9
lab:
  id: "prereq-0.8-servers-ssh"
  url: "https://killercoda.com/kubedojo/scenario/prereq-0.8-servers-ssh"
  duration: "25 min"
  difficulty: "beginner"
  environment: "ubuntu"
---
> **Complexity**: `[QUICK]` - Concepts and a hands-on connection
>
> **Time to Complete**: 25 minutes
>
> **Prerequisites**: [Module 0.5 - Editing Files](../module-0.5-editing-files/)

---

## What You'll Be Able to Do

After this module, you will be able to:
- **Explain** what a server is and why it doesn't need a screen or keyboard
- **Connect** to a remote machine using SSH and navigate it from the terminal
- **Distinguish** between password and key-based SSH authentication and explain why keys are safer
- **Verify** you're on the right machine after connecting (using `hostname`, `whoami`, `pwd`)

---

## Why This Module Matters

Everything you've done so far has been on *your* computer. Your kitchen, your files, your terminal. But in the real world of technology, most of the action happens on computers that are *somewhere else* -- in a data center, in the cloud, in a rack of machines you'll never physically touch.

These other computers are called **servers**, and the way you talk to them is through **SSH**.

When you work with Kubernetes, you'll be managing servers (lots of them). Understanding what servers are and how to connect to them is not optional -- it's fundamental.

---

## What is a Server?

A server is just a computer. That's it. No magic, no mystery.

The word "server" describes what the computer *does*, not what it *is*. A server is a computer whose job is to **serve** things to other computers.

```
Your laptop:
  - Has a screen, keyboard, trackpad
  - Designed for ONE person to sit in front of
  - Runs a graphical interface (windows, icons, mouse)
  - You browse the web, write documents, watch videos

A server:
  - Often has NO screen, keyboard, or mouse
  - Designed to serve MANY users/computers simultaneously
  - Usually runs ONLY a terminal interface (no desktop)
  - It hosts websites, runs databases, processes data
```

### The Kitchen Analogy

Think of it this way:

- **Your laptop** is a home kitchen. You cook for yourself. You eat in the same room where you cook. The "chef" and the "customer" are the same person.

- **A server** is a restaurant kitchen. It exists to prepare food and send it *out* to a dining room full of customers. The kitchen has no dining tables -- that's not its job. Its job is to cook and serve.

When you visit a website, your browser (the customer in the dining room) sends a request to a server (the kitchen in the back). The server prepares the response (cooks the meal) and sends it back to your browser (serves the dish).

---

## Your Laptop vs. a Server

Under the hood, they have the same basic parts:

| Component | Your Laptop | A Typical Server |
|-----------|-------------|-----------------|
| CPU | 4-8 cores | 16-128 cores |
| RAM | 8-32 GB | 64-512 GB |
| Storage | 256 GB - 2 TB | 1 TB - 100 TB+ |
| Screen | Yes | Usually no |
| Keyboard | Yes | Usually no |
| Operating System | macOS/Windows | Linux (almost always) |
| Purpose | One person, many tasks | Many clients, specific tasks |

A server is basically a beefy computer optimized for serving many requests at once, running 24/7, and being managed remotely.

---

## Local vs. Remote

Two words you'll hear constantly:

- **Local** = your computer, right here, in front of you
- **Remote** = a different computer, somewhere else, that you connect to over a network

```
Local:  Your kitchen. You're standing in it.
Remote: A kitchen in another city. You call them on the phone to give orders.
```

When you type `ls` in your terminal right now, that command runs **locally** -- on your computer.

When you connect to a server and type `ls`, that command runs **remotely** -- on the server. But it looks exactly the same in your terminal. That's the beauty of it.

### Quick Check: Local or Remote?

> **Stop and think**: Classify these 5 scenarios as local or remote operations.
> 1. Editing a photo on your laptop's desktop.
> 2. Using SSH to check the logs of a web server in London.
> 3. Running `pwd` in your terminal immediately after opening it.
> 4. Typing `ls` after connecting via `ssh admin@10.0.0.5`.
> 5. Your browser requesting a web page from Wikipedia.

<details>
<summary>Answers</summary>
1. **Local** (happening on the machine in front of you)
2. **Remote** (you are telling a distant server to show its logs)
3. **Local** (you haven't connected to another machine yet)
4. **Remote** (your terminal is now controlling the 10.0.0.5 machine)
5. **Remote** (the Wikipedia server is sending you the page data)
</details>

---

## SSH: Your Secure Tunnel to Remote Kitchens

**SSH** stands for **S**ecure **Sh**ell. It's a program that lets you open a terminal session on a remote computer, securely.

Think of SSH as a **secure phone line to a remote kitchen**. You pick up the phone (open SSH), dial the number (connect to the server), and start giving orders (typing commands). The chef in the remote kitchen carries them out, and you hear the results through the phone.

The "secure" part is important: SSH encrypts the session in transit, so people on the network cannot read the commands and output. It's like having a private, scrambled phone line.

### A Quick Word About Environment Variables

You'll sometimes see things like `$USER` or `$HOME` in commands or documentation. These are **environment variables** -- named boxes that your system fills with useful values automatically.

- `$USER` holds your username
- `$HOME` holds the path to your home directory

Try them out:

```bash
echo $USER
echo $HOME
```

You don't need to set these -- your computer does it for you when you log in. We mention this now because SSH commands often use `$USER`, and you'll see environment variables throughout your career.

### Try it now

Run these commands in your terminal right now:

```bash
echo $USER
echo $HOME
```

> **Pause and predict**: If you connect to a remote server using `ssh chef@192.168.1.100` and then run `echo $USER`, what will it output? Your laptop's username, or `chef`?
>
> <details>
> <summary>Answer</summary>
> It will output <code>chef</code>! When you SSH into a server, the commands run in the context of the remote user. The <code>$USER</code> variable on that server is set to the user you logged in as.
> </details>

### The SSH Command

The basic SSH command looks like this:

```bash
ssh username@ip-address
```

Let's break that down:

- `ssh` -- the program you're running
- `username` -- your account name on the remote server (like your name badge at the remote kitchen)
- `@` -- just a separator (the "at" sign)
- `ip-address` -- the address of the remote server (like the phone number of the kitchen)

A real example might look like:

```bash
ssh chef@192.168.1.100
```

Or with a domain name instead of an IP address:

```bash
ssh chef@kitchen.example.com
```

### What Happens When You Connect

```
1. You type: ssh chef@kitchen.example.com
2. SSH contacts the remote server
3. The server asks: "Who are you? Prove it."
4. You provide proof (password or key -- more on this below)
5. The server says: "Welcome, chef. Here's your terminal."
6. Your prompt changes to show the remote server's name
7. Every command you type now runs on the REMOTE server
8. Type "exit" to disconnect and return to your local terminal
```

Your terminal prompt might change from:

```
yourname@your-laptop ~ $
```

to:

```
chef@remote-server ~ $
```

That's how you know you're connected to a different machine.

---

## Passwords vs. SSH Keys

Two common ways to prove your identity to a remote server are:

### Passwords

The simple way. The server asks for a password, you type it.

```bash
ssh chef@kitchen.example.com
# Server asks: chef@kitchen.example.com's password:
# You type your password (it won't show on screen -- that's normal)
```

Passwords work, but they have problems:
- You have to type them every time
- They can be guessed or stolen
- They're annoying for automated systems

### SSH Keys (The Better Way)

> **Think about it**: Passwords can be guessed, stolen, or phished. What if instead of telling the server a secret word, you could prove your identity with something only you possess — like a physical key that fits a specific lock? That's exactly what SSH keys do. The server never learns your "password" — it just checks if your key fits.

SSH keys work like a lock-and-key system:

```
You have a KEY (private key) -- kept on your computer, never shared.
The server has a LOCK (public key) -- it knows what key fits.

When you connect:
1. You present your key
2. The server checks: "Does this key fit my lock?"
3. If yes: "Come in!" (no password needed)
4. If no: "Access denied."
```

This is like having a physical key to the remote kitchen's door. You don't need to tell anyone a password -- you just unlock the door.

**Generating SSH keys** (you don't need to do this right now, just know how):

```bash
ssh-keygen -t ed25519
```

[This creates two files:](https://github.com/github/docs/blob/main/content/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent.md)
- `~/.ssh/id_ed25519` -- Your **private key** (the key). NEVER share this with anyone.
- `~/.ssh/id_ed25519.pub` -- Your **public key** (the lock). You can share this freely.

You copy the public key to the server, and from then on, you can connect without a password.

> **Think of it this way**: The private key is your house key. The public key is a copy of the lock on your door. You can give the lock to anyone and say "put this on your door." Now your key opens their door too. But nobody can make a key from looking at the lock.

---

## Common SSH Options

| Option | What It Does | Example |
|--------|-------------|---------|
| `-p` | Connect on a different port (default is 22) | `ssh -p 2222 chef@server.com` |
| `-i` | Use a specific key file | `ssh -i ~/.ssh/mykey chef@server.com` |
| `-v` | Verbose mode (shows what's happening -- useful for debugging) | `ssh -v chef@server.com` |

### Mini-Exercise: Build the Command

> **Stop and think**: Write the exact SSH command to connect to the user `admin` on the server `10.0.0.5` using port `2222` and the key file `~/.ssh/work_key`.

<details>
<summary>Answer</summary>

```bash
ssh -p 2222 -i ~/.ssh/work_key admin@10.0.0.5
```
*(Note: the order of `-p` and `-i` doesn't matter, as long as they come before the `user@host` part).*
</details>

---

## The Lifecycle of a Connection

```
Your computer                          Remote server
    |                                       |
    |  --- ssh chef@server.com ---------->  |
    |                                       |  "Connection request received"
    |  <--- "Prove your identity" --------  |
    |                                       |
    |  --- sends key/password ----------->  |
    |                                       |  "Identity confirmed"
    |  <--- "Welcome! Here's a shell" ----  |
    |                                       |
    |  --- ls, pwd, nano, etc. --------->  |  (commands run HERE, on the server)
    |  <--- [ BLANK 1: Predict what happens here ] --- |
    |                                       |
    |  --- [ BLANK 2: How do you disconnect? ] ------> |
    |                                       |  "Goodbye"
    |  (back to local terminal)             |
```

> **Pause and predict**: Fill in the two blanks in the diagram above. What does the server send back after you run a command, and what command do you type to disconnect?
>
> <details>
> <summary>Answers</summary>
> <strong>BLANK 1:</strong> The server sends back the results/output of your commands.<br>
> <strong>BLANK 2:</strong> You type <code>exit</code> to disconnect and return to your local terminal.
> </details>

> **Pause and predict**: If you're SSH'd into a server and you run `rm -rf /home/yourname/projects`, what happens? Does it delete files on your laptop or on the server? This is not a trick question — but it's the kind of mistake that has caused real outages. Always check `hostname` after connecting to confirm you're on the machine you think you are.

**Key insight**: When you're connected via SSH, your terminal *looks* the same, but every command runs on the remote machine. If you create a file, it's created on the server, not your laptop. If you run `pwd`, it shows the server's directory, not yours.

---

## Why This Matters for Kubernetes

Kubernetes runs on servers -- usually many of them. A typical Kubernetes cluster might have:

- 3 servers for the "control plane" (the restaurant management office)
- 10-100+ servers as "worker nodes" (the kitchens that do the actual cooking)

You'll use SSH to connect to these servers, troubleshoot problems, check logs, and manage configurations. The commands you learned in previous modules -- `ls`, `cd`, `nano`, `cat` -- work exactly the same on these remote servers.

---

## Did You Know?

- **SSH is standardized as a secure remote access protocol.** [RFC 4251 defines SSH as a protocol for secure remote login and other secure network services over an insecure network.](https://www.rfc-editor.org/rfc/rfc4251) That is the big reason it [replaced older remote-login tools such as `telnet` for shell access.](https://en.wikipedia.org/wiki/Secure_Shell)

- **[Port 22 is the IANA-assigned default port for SSH.](https://en.wikipedia.org/wiki/Secure_Shell)** That is why many examples use 22 unless an administrator deliberately changes it.

- **SSH is a general-purpose operations tool.** [OpenSSH describes itself as software for remote login and remote command execution](https://github.com/openssh/openssh-portable), which is why you will see SSH used on cloud VMs, internal Linux servers, lab machines, and similar systems.

**References**: RFC 4251, RFC 4250, and the OpenSSH documentation.

---

## Common Mistakes

| Mistake | Why It's a Problem | What to Do Instead |
|---------|-------------------|-------------------|
| Sharing your private key | Anyone with your private key can access your servers | Never share `id_ed25519` (the file WITHOUT `.pub`). Only share the `.pub` file |
| Forgetting you're on a remote server | You might delete files or change things on the wrong machine | Always check your prompt and use `hostname` to verify which machine you're on |
| Typing your password in the wrong field | SSH hides password input (no dots, no asterisks). People think it's broken and type it somewhere visible | When SSH asks for a password, just type it blind and press Enter. It IS receiving your keystrokes |
| Not disconnecting when done | Leaving SSH sessions open wastes server resources and can be a security risk | Type `exit` or press `Ctrl + D` when you're done |
| Panicking when the connection drops | Network interruptions happen -- it doesn't mean something is broken | Just reconnect with the same SSH command. Your files on the server are still there |

---

## Quiz

1. **You SSH into a server and run `hostname` — it shows your laptop name. What happened?**
   <details>
   <summary>Answer</summary>
   You are not actually connected to the remote server! Either the SSH connection failed, or you already typed `exit` and returned to your local terminal without realizing it. Because you ran `hostname` and saw your laptop's name, you confirmed that your commands are currently running locally, not remotely. Always check your prompt and use `hostname` to verify your environment to avoid running destructive commands on the wrong machine.
   </details>

2. **Your colleague asks you to email them your SSH private key so they can quickly log into a server you both manage. What do you say and why?**
   <details>
   <summary>Answer</summary>
   You must say absolutely not. Your private key (e.g., `id_ed25519`) is your personal "house key" and should never be shared with anyone, not even colleagues. If they need access to the server, they should generate their own SSH key pair and give you their *public* key (`id_ed25519.pub`), which you can then add to the server's allowed list. This ensures everyone's access remains secure and allows you to revoke their access later without changing your own key.
   </details>

3. **You are configuring a new deployment server and need it to connect to your database server securely without a password. Which key (public or private) do you place on the database server, and why?**
   <details>
   <summary>Answer</summary>
   You place the public key on the database server (acting as the lock). The private key stays on the deployment server (acting as the key). The server checks if the connecting machine's private key matches its stored public key. Knowing the public key doesn't help anyone impersonate the deployment server, keeping the connection secure.
   </details>

4. **When you're connected to a remote server via SSH and you type `touch recipe.txt`, where is the file created?**
   <details>
   <summary>Answer</summary>
   On the remote server, not on your local machine. When you're connected via SSH, every command you type runs on the remote server. The file `recipe.txt` is created on the server's file system. Your local machine doesn't get a copy. To verify which machine you're on, check the terminal prompt or type `hostname`.
   </details>

5. **Progressive Difficulty: You need to automate deployments from a CI (Continuous Integration) server to 50 production machines. Would you use password or key-based auth? Explain your reasoning.**
   <details>
   <summary>Answer</summary>
   You must use key-based authentication. If you used passwords, an automated script would either get stuck waiting for a human to type the password 50 times, or you would have to hardcode the password directly into the script (which is a massive security risk). With SSH keys, the CI server can securely hold a private key, and the 50 production machines can be configured to trust its public key. This allows the automated system to connect instantly and securely without human intervention, making deployments both fast and secure.
   </details>

---

## Hands-On Exercise: SSH to Localhost

We'll practice SSH by connecting to your own computer. This might sound pointless ("I'm already here!"), but it demonstrates exactly how SSH works -- and the experience is identical to connecting to a real remote server.

### On macOS:

First, enable Remote Login (SSH) if it's not already enabled:

1. Open **System Settings** (or System Preferences on older macOS)
2. Go to **General > Sharing**
3. Turn on **Remote Login**

Now, in your terminal:

```bash
ssh localhost
```

You'll see something like:

```
The authenticity of host 'localhost (127.0.0.1)' can't be established.
ED25519 key fingerprint is SHA256:AbCdEf123456...
Are you sure you want to continue connecting (yes/no)?
```

Type `yes` and press Enter. (This only appears the first time you connect to a new server. The computer is saying "I've never talked to this server before -- are you sure it's legit?")

Enter your Mac password when prompted.

Now you're "connected." Try:

```bash
hostname
whoami
pwd
ls
echo "Hello from SSH!"
```

Everything looks the same because you're SSH-ing to yourself. But the mechanism is identical to connecting to a server across the world.

To disconnect:

```bash
exit
```

### On Linux:

On Linux, SSH server defaults vary by distribution and image. For example, many desktop installs do not expose an SSH server until you install it, while server-oriented images often make it available during setup. On Debian or Ubuntu systems where OpenSSH Server is missing or not running, you can install and start it with:

```bash
sudo apt update
sudo apt install -y openssh-server
sudo systemctl enable --now ssh
```

Then:

```bash
ssh localhost
```

Follow the same steps as macOS above.

### On Windows:

SSH to localhost is trickier on Windows. Instead, just practice the command syntax:

```
# This is what connecting to a real server would look like:
ssh yourname@192.168.1.100

# You would see:
yourname@192.168.1.100's password:

# After entering the password:
yourname@remote-server:~$

# Now every command runs on the remote server.
# Type "exit" to disconnect.
```

### What Would Happen With a Real Server

If you had a cloud server (you'll get one when you start the Kubernetes track), the experience would be:

```bash
# Connect to a server in the cloud
ssh ubuntu@54.123.45.67

# You'd see:
ubuntu@ip-54-123-45-67:~$

# Now you're inside a Linux server in a data center somewhere
# Every command runs there:
ls          # Shows files on the server
pwd         # Shows your path on the server
nano        # Opens nano on the server
cat /etc/os-release    # Shows the server's operating system

# Disconnect when done
exit
```

It would look, feel, and work exactly like the localhost exercise. The main difference is the physical location of the computer.

**Success criteria**: You must run `hostname` in your terminal *before* connecting via SSH and record the output. Then, successfully open the SSH connection and run `hostname` again *after* connecting. If you are using `ssh localhost`, the hostname will usually stay the same because you are connecting back into the same machine through SSH; the proof is that you established an SSH session, ran commands inside it, and then disconnected cleanly. If you are connecting to a different machine, `hostname` should change. In either case, run at least one other command to verify the file system and then disconnect properly.

---

## What's Next?

**Next Module**: [Module 0.9: Software and Packages](../module-0.9-software-and-packages/) — Learn how software gets installed on your computer, what package managers are, and how to install tools from the terminal.

---

> **You just used a tool that senior engineers use every day. You belong here.**

## Sources

- [GitHub Docs Source: Generating a New SSH Key](https://github.com/github/docs/blob/main/content/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent.md) — Practical reference for generating an Ed25519 SSH key and the usual default key file locations.
- [RFC 4251: The Secure Shell (SSH) Protocol Architecture](https://www.rfc-editor.org/rfc/rfc4251) — Standards document defining SSH as secure remote login and related secure network services over insecure networks.
- [Secure Shell](https://en.wikipedia.org/wiki/Secure_Shell) — Background reference covering SSH history, its relationship to Telnet, and default port 22.
- [Portable OpenSSH](https://github.com/openssh/openssh-portable) — Upstream OpenSSH project describing remote login, remote command execution, and related SSH operations.
