# Spatial Backend - CI/CD API Gateway Pipeline

This project provides an automated way to deploy Kong (an API gateway) along with its dependencies using Ansible and Docker Compose. The deployment includes the Kong service, a PostgreSQL database, and Konga, a web-based GUI for managing and monitoring Kong.

## Prerequisites
- **Git**
- **Ansible** installed on your local machine.
- Ensure the remote server **does not** have **Docker** pre-installed, as the playbook will handle Docker setup.

## Setup and Configuration

**Step 1: Clone the Repository**

Clone the repository to your local machine:

   ```bash
   git clone https://github.com/mobile-cloud-computing/spatial-backend.git
cd spatial-backend/ci-cd-api-gateway-pipleine/ansible
   ```

**Step 2: Replace files in the Ansible directory**

Replace the `id_rsa` file with your `ssh_private_key_file` in the Ansible directory 

**Note**: Remember to rename the `ssh_private_key_file` as `id_rsa`

**Step 3: Update the Inventory File**

The inventory file specifies the target server details:

  ```ini
<remote_server_ip> ansible_ssh_user=<username> ansible_ssh_private_key_file=id_rsa
  ```

`<remote_server_ip>`: Replace with your server's IP address (e.g., 172.17.90.181).

`<username>`: Replace with the SSH user on your server (e.g., ubuntu).

For example:

 ```ini
172.17.90.181 ansible_ssh_user=ubuntu ansible_ssh_private_key_file=id_rsa
 ```

**Step 4: Customize the Configuration**

1. Update the `myconf` file
   
Replace the `server name` with your target VM's IP.

 ```ini
    server_name 172.17.90.181;
 ```
**Note**: Remember to change the server name in the entire file.

2. Docker Configuration
   
If you want to customize Docker settings (e.g., network options, storage drivers), update the content in playbook.yaml under the Creating a file with content task:

```yaml
  - name: Creating a file with content
    copy:
      dest: "/etc/docker/daemon.json"
      content: |
        {
          "bip": "192.168.67.1/24",
          "fixed-cidr": "192.168.67.0/24",
          "storage-driver": "overlay2",
          "mtu": 1400,
          ...
        }
```
3. Docker Compose Services
   
Open the docker-compose.yml file to customize the Kong, PostgreSQL, and Konga services. Update any configuration, such as environment variables, ports, or volumes.

**Step 5: Run the Ansible Playbook**

From the ansible directory, run the playbook to set up the server:

```bash
ansible-playbook -i inventory playbook.yaml
```

This command will:

1. Connect to the remote server specified in the `inventory` file.
2. Install Docker, Docker Compose, and other necessary dependencies.
3. Deploy the Kong, PostgreSQL, and Konga services using Docker Compose.

**Step 6: Verify the Deployment**

- Kong Gateway: Kong's proxy and admin endpoints should be available at the following ports on the server:
  
  - Proxy: http://<remote_server_ip>:8000
  - Proxy SSL: https://<remote_server_ip>:8443
  - Admin: http://<remote_server_ip>:8001
  - Admin SSL: https://<remote_server_ip>:8444

- Konga (Web GUI): Accessible on:
  
```arduino
http://<remote_server_ip>:1337
```

**Step 7: Configuration of Nginx**

The playbook also installs and configures Nginx. If you need to modify Nginx settings, edit the `myconf` file, which is copied to `/etc/nginx/sites-enabled/myconf` on the remote server. 

Copy the `nginx.conf` file (from the `Latest Configs` folder in the repo) to the `/etc/nginx` folder on the remote server to configure the NGINX with the latest implementations. If you need to modify Nginx settings, edit the `nginx.conf` file.

**Step 8: Restore Kong Configuration Using Konga GUI**

After deploying the Kong services, you can restore your previously saved configuration using the Konga GUI by following these steps:

1. Open Konga:
   
- Navigate to the Konga web interface on your browser:
  
```arduino
http://<remote_server_ip>:1337
```

2. Login to Konga:
   
- If this is your first time accessing Konga, you’ll be prompted to create a new user account.

3. Connect to Kong
   
- After logging in, click on "Connections" in the sidebar.
- Click "New Connection".
- Provide a name (e.g., Kong-Gateway), and use the Kong Admin URL:
  
```arduino
http://<remote_server_ip>:8001
```
- Click "Connect" to establish the connection with Kong.

4. Upload the Snapshot:
   
- Click on "Snapshots" in the sidebar.
- Click on "Upload Snapshot".
- Choose the `02_10_2024_SNAPSHOT.json` file from the `Latest Configs` folder in your local repository.
- Click "Upload" to restore the configuration.

5. Apply the Snapshot:
   
- After the snapshot is uploaded, click "Restore" to apply all the services, routes, and plugins defined in the snapshot to the Kong Gateway.

## Troubleshooting

1. Connection Issues:
   
-Ensure the IP address and SSH credentials in the inventory file are correct.
-Verify the SSH key (id_rsa) has the correct permissions: chmod 600 id_rsa.

3. Docker or Ansible Errors:
   
- Confirm the remote server can access the Docker repository.
- Check if the server has sufficient resources (memory and CPU).

3. Service Not Starting:
   
- Use docker compose logs <service_name> to view logs of a specific service.
- Check for port conflicts or missing environment variables.
