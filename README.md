# Jenkins Monitoring Setup on Azure VM using Docker, Prometheus, and Grafana

## Objective

Deploy Jenkins, Prometheus, and Grafana on an Azure Linux Virtual Machine using Docker containers and monitor Jenkins build metrics through Prometheus and Grafana dashboards.

---

## Architecture

Jenkins Container → Prometheus Metrics Endpoint (/prometheus/) → Prometheus → Grafana Dashboard

Components:

* Azure Linux VM
* Docker
* Jenkins LTS Container
* Prometheus Container
* Grafana Container
* Jenkins Prometheus Plugin

---

## Step 1: Deploy Jenkins Container

Pull Jenkins image:

```bash
docker pull jenkins/jenkins:lts
```

Run Jenkins:

```bash
docker run -d \
--name jenkins \
-p 8080:8080 \
-p 50000:50000 \
-v jenkins_home:/var/jenkins_home \
jenkins/jenkins:lts
```

Verify:

```bash
docker ps
```

Access Jenkins:

```text
http://<VM-PUBLIC-IP>:8080
```

---

## Step 2: Restore Existing Jenkins Data

Backup file:

```text
jenkins-backup.tar.gz
```

Stop Jenkins:

```bash
docker stop jenkins
```

Extract backup:

```bash
mkdir ~/jenkins_restore
tar -xzvf jenkins-backup.tar.gz -C ~/jenkins_restore
```

Copy Jenkins data:

```bash
sudo cp -a ~/jenkins_restore/var/lib/jenkins/. \
/var/lib/docker/volumes/<jenkins-volume>/_data/
```

Set permissions:

```bash
sudo chown -R 1000:1000 \
/var/lib/docker/volumes/<jenkins-volume>/_data
```

Start Jenkins:

```bash
docker start jenkins
```

Validation:

```bash
docker logs -f jenkins
```

Expected output:

```text
Jenkins is fully up and running
```

---

## Step 3: Install Jenkins Prometheus Plugin

Navigate:

```text
Manage Jenkins
→ Plugins
→ Available Plugins
→ Prometheus Metrics
```

Install plugin and restart Jenkins.

Metrics endpoint:

```text
http://<VM-PUBLIC-IP>:8080/prometheus/
```

Validation:

```bash
curl http://localhost:8080/prometheus/ | head
```

Expected output:

```text
# HELP
# TYPE
default_jenkins_builds_health_score
```

---

## Step 4: Deploy Prometheus Container

Run Prometheus:

```bash
docker run -d \
--name prometheus \
-p 9090:9090 \
-v $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml \
prom/prometheus
```

---

## Step 5: Configure Jenkins Scraping

Update prometheus.yml:

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets:
          - 'localhost:9090'

  - job_name: 'jenkins'
    metrics_path: '/prometheus/'
    static_configs:
      - targets:
          - '172.17.0.1:8080'
```

Important:

```text
localhost:8080 does not work from inside the Prometheus container.
```

Reason:

```text
localhost inside a container refers to the container itself.
```

Use Docker bridge IP or Docker networking.

Restart Prometheus:

```bash
docker restart prometheus
```

---

## Step 6: Validate Prometheus Scraping

Open:

```text
http://<VM-PUBLIC-IP>:9090/targets
```

Expected:

```text
jenkins → UP
```

Test PromQL:

```promql
default_jenkins_builds_last_build_result_ordinal
```

Result:

```text
default_jenkins_builds_last_build_result_ordinal{
  jenkins_job="proj2-jenkins-pipeline"
}
```

---

## Step 7: Deploy Grafana

Run Grafana:

```bash
docker run -d \
--name grafana \
-p 3000:3000 \
grafana/grafana
```

Access:

```text
http://<VM-PUBLIC-IP>:3000
```

Default credentials:

```text
admin/admin
```

---

## Step 8: Configure Grafana Data Source

Navigate:

```text
Connections
→ Data Sources
→ Prometheus
```

Prometheus URL:

```text
http://<VM-PUBLIC-IP>:9090
```

Save and Test.

---

## Step 9: Build Jenkins Dashboard

Example PromQL queries:

Build Result:

```promql
default_jenkins_builds_last_build_result_ordinal
```

Health Score:

```promql
default_jenkins_builds_health_score
```

Available Builds:

```promql
default_jenkins_builds_available_builds_count
```

Legend:

```text
{{jenkins_job}}
```

---

## Troubleshooting Performed

Issue 1:
Jenkins inaccessible via VM IP.

Resolution:

* Verified Docker port mapping.
* Opened Azure NSG port 8080.
* Verified Jenkins locally using curl.

Issue 2:
Prometheus unable to scrape Jenkins.

Root Cause:

* Target configured as localhost:8080.

Resolution:

* Changed target to Docker host IP.
* Restarted Prometheus.

Issue 3:
Grafana displayed no Jenkins metrics.

Root Cause:

* Imported dashboard expected different metric names.

Resolution:

* Queried Jenkins Prometheus plugin metrics directly.
* Created custom Grafana panels.

---

## Outcome

Successfully migrated Jenkins to Azure VM Docker container, restored historical Jenkins data, exposed Jenkins metrics using Prometheus plugin, configured Prometheus scraping, and visualized Jenkins build health and pipeline metrics in Grafana.

Technologies Used:

* Azure Virtual Machines
* Docker
* Jenkins
* Prometheus
* Grafana
* Linux Administration
* Monitoring & Observability
* CI/CD
