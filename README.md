# README - Hướng dẫn triển khai ODC Explorer với Docker Compose

## Giới thiệu

Tài liệu này hướng dẫn cách khởi tạo và vận hành hệ thống **ODC Explorer** bằng Docker Compose, bao gồm:

- Tải source code Datacube Explorer từ GitHub
- Build Docker image
- Khởi động / dừng container
- Khởi tạo giao diện Explorer
- Index dữ liệu viễn thám
- Nạp Dataset EO3
- Cập nhật dữ liệu hiển thị trên Web Explorer

---

# 1. Tải Datacube Explorer từ GitHub

Clone source code từ GitHub:

```bash
git clone https://github.com/opendatacube/datacube-explorer.git
```

# 2. Build Docker Images

Lệnh dưới đây sẽ build toàn bộ Docker image được định nghĩa trong `docker-compose.yml`.

```bash
docker compose build
```

---

# 3. Khởi động Containers

Khởi chạy toàn bộ container ở chế độ nền (`detached mode`).

```bash
docker compose up -d
```

Kiểm tra trạng thái container:

```bash
docker compose ps
```

---

# 4. Dừng và gỡ Containers

Dừng và xoá toàn bộ container.

```bash
docker compose down
```

> Không cần thêm `-d` cho lệnh `down`.

---

# 5. Khởi tạo giao diện ODC Explorer

## Cách khuyến nghị: dùng profile

```bash
docker compose --profile setup up --force-recreate explorer-init
```

Lệnh này sẽ:

- Khởi tạo database Explorer
- Chuẩn bị metadata cần thiết
- Tạo cấu hình ban đầu cho giao diện Explorer

---

## Chạy trực tiếp

```bash
docker compose run --rm explorer cubedash-gen -v --init
```

---

# 6. Nạp Product vào Datacube (Indexing)

Thêm định nghĩa product từ file YAML.

```bash
docker compose exec odc-server datacube product add /data/product.yaml
```

---

# 7. Nạp Dataset EO3

Nạp dữ liệu không gian thực tế theo chuẩn EO3.

```bash
docker compose exec odc-server datacube dataset add /data/dataset.yaml
```

---

# 8. Cập nhật dữ liệu lên Web Explorer

Sau khi index dataset, cần cập nhật lại Explorer để dữ liệu hiển thị trên giao diện web.

## Cách khuyến nghị: dùng profile

```bash
docker compose --profile tools up --force-recreate explorer-index
```

---

## Chạy trực tiếp

```bash
docker compose run --rm explorer cubedash-gen --all
```

---

# Quy trình đầy đủ

Thứ tự chạy đề xuất:

```bash
# Clone source code
git clone https://github.com/opendatacube/datacube-explorer.git

# Build images
docker compose build

# Khởi động hệ thống
docker compose up -d

# Khởi tạo explorer
docker compose --profile setup up --force-recreate explorer-init

# Nạp product
docker compose exec odc-server datacube product add /data/product.yaml

# Nạp dataset
docker compose exec odc-server datacube dataset add /data/dataset.yaml

# Cập nhật explorer
docker compose --profile tools up --force-recreate explorer-index
```

---
