# README - Hướng dẫn Triển khai ODC Server với Kubernetes (Kustomize)

## Giới thiệu

Tài liệu này hướng dẫn cách triển khai hệ thống **ODC Server** trên **Kubernetes** sử dụng **Kustomize** để quản lý cấu hình. Hệ thống bao gồm:

- **PostgreSQL**: Cơ sở dữ liệu chính
- **MinIO**: Dịch vụ lưu trữ object (S3 compatible)
- **ODC Server**: Máy chủ Datacube
- **JupyterHub**: Môi trường notebook tương tác
- **ODC Explorer**: Giao diện web để khám phá dữ liệu
- **Ingress**: Điều hướng traffic và expose service

### Tổng quan Kiến trúc (Architecture Overview)

Hệ thống hoạt động dựa trên sự tương tác chặt chẽ giữa các thành phần:

- **JupyterHub** cung cấp môi trường lập trình trực tuyến cho người dùng.
- Các notebook từ JupyterHub sẽ gọi API đến **ODC Server** để xử lý dữ liệu.
- **ODC Server** đóng vai trò trung tâm, truy vấn thông tin metadata (vị trí, thời gian) từ **PostgreSQL** và tải trực tiếp dữ liệu ảnh viễn thám gốc (GeoTIFF, NetCDF) từ **MinIO**.
- Tất cả các dịch vụ giao tiếp với bên ngoài đều được điều hướng qua **NGINX Ingress**.

---

## Yêu cầu Tiên quyết (Prerequisites)

### 1. Kubernetes Cluster

- Kubernetes v1.20 trở lên
- `kubectl` CLI được cấu hình để truy cập cluster
- Kiểm tra kết nối:
  ```bash
  kubectl cluster-info
  kubectl get nodes
  ```

### 2. NGINX Ingress Controller

Cài đặt NGINX Ingress Controller để expose các service:

```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml
```

Xác nhận cài đặt:

```bash
kubectl get pods -n ingress-nginx
```

### 3. Cấu hình Local Hosts

Để truy cập các service qua hostname, thêm các dòng sau vào file **hosts**:

**Windows** (`C:\Windows\System32\drivers\etc\hosts`):

```
127.0.0.1 explorer.odc-server.local
127.0.0.1 jupyter.odc-server.local
127.0.0.1 minio.odc-server.local
```

**Linux/macOS** (`/etc/hosts`):

```
127.0.0.1 explorer.odc-server.local
127.0.0.1 jupyter.odc-server.local
127.0.0.1 minio.odc-server.local
```

> Nếu dùng cluster remote, thay `127.0.0.1` bằng IP của cluster hoặc load balancer.

---

## Cấu trúc Dự án

```
kustomize/
├── base/                           # Base manifests (dùng cho tất cả môi trường)
│   ├── namespace.yaml              # Tạo namespace 'odc-system'
│   ├── 01-postgres-core.yaml       # PostgreSQL StatefulSet & PVC
│   ├── 02-minio-storage.yaml       # MinIO Deployment & Service
│   ├── 03-odc-server.yaml          # ODC Server Deployment
│   ├── 04-jupyter-rbac.yaml        # RBAC cho Jupyter
│   ├── 05-jupyter-hub.yaml         # JupyterHub Deployment
│   ├── 06-jupyter-proxy.yaml       # Jupyter Proxy Service
│   ├── 07-ingress.yaml             # Ingress rules
│   ├── 08-odc-explorer.yaml        # ODC Explorer Deployment
│   ├── jupyterhub_config.py        # Cấu hình JupyterHub
│   └── kustomization.yaml          # Danh sách resources
└── overlays/
    └── dev/                        # Cấu hình cho môi trường dev
        ├── kustomization.yaml      # Patches & customizations
        └── .env                    # Biến môi trường
```

### Base Resources

- **namespace.yaml**: Tạo namespace `odc-system` để cô lập resources
- **PostgreSQL**: Database lưu trữ metadata, được bảo vệ bằng PersistentVolumeClaim
- **MinIO**: Object storage tương thích S3 cho dữ liệu viễn thám
- **ODC Server**: API server chính
- **JupyterHub**: Cung cấp Jupyter notebooks cho users
- **ODC Explorer**: Giao diện web để khám phá dữ liệu
- **Ingress**: Expose services qua HTTP/HTTPS

---

## Triển khai (Deployment)

### 1. Xem Manifest (Preview)

Trước khi áp dụng, kiểm tra các resource sẽ được tạo:

```bash
kubectl kustomize kustomize/overlays/dev
```

### 2. Triển khai sang Cluster

Áp dụng toàn bộ cấu hình:

```bash
kubectl apply -k kustomize/overlays/dev
```

### 3. Kiểm tra Trạng thái

Xem toàn bộ resource trong namespace `odc-system`:

```bash
# Liệt kê tất cả pods
kubectl get pods -n odc-system

# Xem pods chi tiết
kubectl get pods -n odc-system -o wide

# Theo dõi pods (live monitoring)
kubectl get pods -n odc-system -w
```

### 4. Xem Log của Pods

```bash
# Log của ODC Server
kubectl logs -n odc-system -l app=odc-server -f

# Log của PostgreSQL
kubectl logs -n odc-system -l app=postgres -f

# Log của MinIO
kubectl logs -n odc-system -l app=minio -f

# Log của JupyterHub
kubectl logs -n odc-system -l app=jupyterhub -f
```

---

## Truy cập Dịch vụ

Sau khi triển khai thành công, các dịch vụ sẽ có sẵn tại:

| Dịch vụ           | URL                              | Chức năng                      |
| ----------------- | -------------------------------- | ------------------------------ |
| **ODC Explorer**  | http://explorer.odc-server.local | Giao diện web khám phá dữ liệu |
| **JupyterHub**    | http://jupyter.odc-server.local  | Notebooks tương tác            |
| **MinIO Console** | http://minio.odc-server.local    | Quản lý object storage         |

### Tìm địa chỉ IP (Nếu chưa cấu hình hosts)

```bash
kubectl get ingress -n odc-system -o wide
```

---

## Cấu hình (Configuration)

### File `.env` (Biến môi trường)

Cập nhật file [kustomize/overlays/dev/.env](kustomize/overlays/dev/.env) để tùy chỉnh cấu hình:

```bash
# Database
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=odc

# MinIO
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin
MINIO_REGION=us-east-1

# ODC Server
ODC_ENVIRONMENT=dev
LOG_LEVEL=INFO
```

### Cập nhật Cấu hình

Sau khi chỉnh sửa `.env`, áp dụng lại:

```bash
kubectl apply -k kustomize/overlays/dev
```

---

## Quản lý Dữ liệu

### 1. Nạp Product (Indexing)

Trước khi nạp Product, bạn cần chuyển file định nghĩa (YAML) từ máy tính local vào bên trong Pod của ODC Server.

**Bước 1:** Copy file từ local vào thư mục `/tmp` của Pod:

```bash
# Lấy tên pod ODC Server hiện tại
POD_NAME=$(kubectl get pods -n odc-system -l app=odc-server -o jsonpath='{.items[0].metadata.name}')

# Copy file vào pod
kubectl cp ./sentinel2_product.yaml odc-system/$POD_NAME:/tmp/sentinel2_product.yaml
```

Thêm định nghĩa product từ file YAML:

```bash
kubectl exec -it -n odc-system $POD_NAME -- \
  datacube product add /tmp/sentinel2_product.yaml
```

### 2. Nạp Dataset

Nạp dữ liệu EO3:

```bash
kubectl exec -it -n odc-system deployment/odc-server -- \
  datacube dataset add /data/dataset.yaml
```

### 3. Khởi tạo ODC Explorer

```bash
kubectl exec -it -n odc-system deployment/odc-server -- \
  cubedash-gen -v --init
```

### 4. Cập nhật Explorer

Sau khi index dataset:

```bash
kubectl exec -it -n odc-system deployment/odc-server -- \
  cubedash-gen --all
```

---

## Scaling & Customization

### Tăng Replicas

Để tăng số lượng pods của một deployment:

```bash
# Tăng ODC Server replicas
kubectl scale deployment/odc-server -n odc-system --replicas=3

# Tăng JupyterHub replicas
kubectl scale deployment/jupyterhub -n odc-system --replicas=2
```

### Tùy chỉnh qua Kustomize

Chỉnh sửa [kustomize/overlays/dev/kustomization.yaml](kustomize/overlays/dev/kustomization.yaml) để:

- Patch resources
- Thay đổi image versions
- Cập nhật ConfigMap/Secrets
- Thêm annotations, labels

---

## Xoá Triển khai

Để xoá toàn bộ resources khỏi cluster:

```bash
kubectl delete -k kustomize/overlays/dev
```

> **Cảnh báo**: Lệnh này sẽ xoá tất cả data. Hãy backup trước khi xoá.

---

## Troubleshooting

### Pods không khởi động

```bash
# Xem mô tả pods để tìm lỗi
kubectl describe pod -n odc-system <pod-name>

# Xem event của namespace
kubectl get events -n odc-system --sort-by='.lastTimestamp'
```

### Service không thể truy cập

```bash
# Kiểm tra Service
kubectl get svc -n odc-system

# Kiểm tra Ingress
kubectl get ingress -n odc-system

# Kiểm tra DNS
kubectl exec -it -n odc-system <pod-name> -- nslookup explorer.odc-server.local
```

### PersistentVolume không available

```bash
# Xem PV và PVC
kubectl get pv
kubectl get pvc -n odc-system

# Xem chi tiết PVC
kubectl describe pvc -n odc-system
```
