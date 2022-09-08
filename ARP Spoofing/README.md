# BTP


## Setting up VM

### Before booting up for the first time

I am using kubuntu machine as a host OS. This probably doesn't make any difference in the workflow since most of the work is carried out in the mininet VM. But I'm just mentioning this for completeness. I spent too much time setting this up due to some strange errors. So, I thought documenting this might help me in the future or someone else.

In this section, I'll describe the steps to properly set up the mininet VM to make development easier, e.g., password-less login, internet access in VM, etc...

- Download the mininet VM of your choice from [here](https://github.com/mininet/mininet/releases). I used [Ubuntu 20.04 VM](https://github.com/mininet/mininet/releases/download/2.3.0/mininet-2.3.0-210211-ubuntu-20.04.1-legacy-server-amd64-ovf.zip).
- I assume Oracle VirtualBox is already installed on the host machine. Unzip the release files and open the OVF file with VirtualBox.
- After creating the VM, open the VM settings window. Click on the networks tab.
  ![Settings Window](https://i.imgur.com/wB2dCHR.png)
- Enable **Adapter 1** and Attach it to **NAT**. Choose `Paravirtualized Network (virto-net)` as the adapter type. (I tried the default Intel adapter, but it didn't work). Adding this adapter enables VM to access the internet.
- Click on Port Forwarding, and in the following window, create a new rule by clicking on the green button at the top. (marked in red below).
  - ![Port forwarding rule](https://i.imgur.com/tMgvcxz.png)
  - Set the Host port to `2222` and the Guest port to `22`. We'll come back to this later.
- Now go back to the Settings window and enable **Adapter 2**. Attach it to **Host-only Adapter**. Click `OK.`
- Open **Host Network Manager** from the **File** menu. Choose a fixed IP starting with `192.168..` and enter it in the IP4 address field. Note this IP since we use it in further steps again.
    ![](https://i.imgur.com/qzvXwX1.png)

### Logging in for the first time

- Start the VM and enter the credentials.
  - Username: `mininet`
  - Password: `mininet`
- The screen might feel small and not very usable. Bear with it. We're going to fix this in a few steps.
- Enter `ifconfig -a` and make sure that one of the interfaces has the IP you set above. It is **Host-only Adapter's** IP. The NAT adapter is the other interface (not the `lo`).

  ```
  mininet@mininet-vm:/etc/netplan$ ifconfig -a
  eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
      inet 10.0.2.15  netmask 255.255.255.0  broadcast 10.0.2.255
      ether 08:00:27:c9:c3:97  txqueuelen 1000  (Ethernet)
      RX packets 405  bytes 34229 (34.2 KB)
      RX errors 0  dropped 0  overruns 0  frame 0
      TX packets 347  bytes 36013 (36.0 KB)
      TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

  eth1: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
      inet 192.168.56.12  netmask 255.240.0.0  broadcast 192.175.255.255
      ether 08:00:27:0d:d3:be  txqueuelen 1000  (Ethernet)
      RX packets 0  bytes 0 (0.0 B)
      RX errors 0  dropped 0  overruns 0  frame 0
      TX packets 0  bytes 0 (0.0 B)
      TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

  ```

  - Here, `eth0` belongs to NAT, and `eth1` belongs to the Host-Only adapter.

- Now, create a file named `02-netcfg.yaml` in the `/etc/netplan` directory (I think the file name doesn't matter, but anyway).

  ```yaml
  network:
    version: 2
    renderer: networkd
    ethernets:
      eth0:
        dhcp4: yes
      eth1:
        dhcp4: no
        addresses: [192.168.56.12/12]
  ```

  - Set your fixed IP address in the addresses array above. Note that the keys `eth0` and `eth1` are the interfaces discussed above. If your VM's interfaces are different, replace `eth0` and `eth1` with them.

- Finally, Run the below commands to apply these changes.

    ```bash=
    sudo netplan generate
    sudo netplan apply
    ```

- Now, you can log in to the VM from the host like below.
  ```
  ❯ ssh -p 2222 mininet@192.168.56.12
  mininet@192.168.56.12's password:
  ```

### Password-less Login (SSH key-setup)

- Cool, now we can log in to the VM, but we must type the password every time we log in. Let's make it easier. Generate an ssh-key on your host machine with `ssh-keygen` (see below for sample output and the prompts).
  ```
  ❯ ssh-keygen -t ed25519
  Generating public/private ed25519 key pair.
  Enter file in which to save the key (/home/appaji/.ssh/id_ed25519): /home/appaji/.ssh/mininet
  Enter passphrase (empty for no passphrase):
  Enter same passphrase again:
  Your identification has been saved in /home/appaji/.ssh/mininet
  Your public key has been saved in /home/appaji/.ssh/mininet.pub
  The key fingerprint is:
  SHA256:aLxb6zV+uK+CeLEK4gd+AL4n3+NtWZGbAMEcWzQl1qk appaji@BlackBox
  The key's randomart image is:
  +--[ED25519 256]--+
  |    oo+*o..      |
  |     ++ oo       |
  |     .. . .      |
  |.    . E o       |
  |o     + S +      |
  | +   ... +       |
  |o =  ..++ o.     |
  |.= =o.==.+...    |
  | .*.o=+oo.+=.    |
  +----[SHA256]-----+
  ```
  - As you can see, I am saving the key at: `/home/appaji/.ssh/mininet`.
- Now copy this key to the VM with `ssh-copy-id`.

  ```
  ❯ ssh-copy-id -i ~/.ssh/mininet.pub mininet
  /usr/bin/ssh-copy-id: INFO: Source of key(s) to be installed: "/home/appaji/.ssh/mininet.pub"
  /usr/bin/ssh-copy-id: INFO: attempting to log in with the new key(s), to filter out any that are already installed
  /usr/bin/ssh-copy-id: INFO: 1 key(s) remain to be installed -- if you are prompted now it is to install the new keys
  mininet@192.168.56.12's password:

  Number of key(s) added: 1

  Now try logging into the machine with: "ssh 'mininet'"
  and check to ensure that only the key(s) you wanted were added.
  ```

  - Path of the key can be specified explicitly with the `-i' flag.

- We're almost done. Now, add the following lines to your host machine's `~/.ssh/config` file.
  ```
  Host mininet
    HostName 192.168.56.12
    User mininet
    Port 2222
    ForwardX11Trusted yes
    IdentityFile /home/appaji/.ssh/mininet
  ```
  - Replace `192.168.56.12` and `/home/appaji/.ssh/mininet` with your fixed IP and your ssh key path, respectively.
- And we're done. :sparkles:
- Now, you can log in to the VM with `ssh mininet` without a password.

:::info
:bulb: **Tip**: Use `sudo -E` instead of `sudo` for any sudo commands. X11 forwarding needs some environment variables only available in `mininet` user's env, but not in root's env.
:::


## ARP Spoofing

First of all, let's discuss ARP briefly. ARP stands for Address Resolution Protocol (don't say ARP protocol because ARP already includes protocol :sweat_smile:).

Inside a network, hosts communicate using MAC addresses. Communication between different networks is carried out through Network Address Translation (NAT). ARP is used to get a particular host's MAC address with their IP address.

ARP includes two types of operations:
1. **Request**: The host broadcasts a message asking who has a particular IP address.
2. **Response**: The host with the IP corresponding to a request responds with its IP address.

### Attack

Fundamentally, ARP is flawed, but we don't have a choice.
- Hosts do not verify whether the packet came from the host mentioned in the packet's header.
- Hosts act on a response even if it did not request the corresponding IP.

We can implement digital signatures to solve the first problem and a timeout for the second issue. But the thing is, ARP is used on very low-end and high-end CPUs. Implementing digital signatures.

### Response Spoofing

![](https://i.imgur.com/JFtH9CQ.png)

We will utilize the fact that hosts do not verify whether the sender is actually the sender or not. We'll send spoofed response packets in which we corrupt the sender's address.

```python=
def spoof(victim2_MAC, victim1_MAC):
    scapy.send(scapy.ARP(op=2, pdst=victim1_IP, psrc=victim2_IP, hwdst=victim1_MAC))
    scapy.send(scapy.ARP(op=2, pdst=victim2_IP, psrc=victim1_IP, hwdst=victim2_MAC))
```

We're sending two packets in which we're setting the fake source address.
