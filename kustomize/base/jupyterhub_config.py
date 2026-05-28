import os
from traitlets.config import get_config

c = get_config()

c.JupyterHub.spawner_class = 'kubespawner.KubeSpawner'

# Xác thực: Dùng DummyAuthenticator để test (đăng nhập user bất kỳ, pass: odc123)
c.JupyterHub.authenticator_class = 'jupyterhub.auth.DummyAuthenticator'
c.DummyAuthenticator.password = "odc123"

c.ConfigurableHTTPProxy.should_start = False
c.ConfigurableHTTPProxy.api_url = 'http://jupyterhub-proxy-public-svc:8001'
c.ConfigurableHTTPProxy.auth_token = os.environ.get('CONFIGPROXY_AUTH_TOKEN')

# --- KHỐI CẤU HÌNH MẠNG CHUẨN KUBERNETES ---
c.JupyterHub.hub_bind_url = 'http://0.0.0.0:8081'
c.JupyterHub.hub_connect_url = 'http://jupyterhub-hub-svc:8081'
c.Spawner.hub_connect_url = 'http://jupyterhub-hub-svc:8081'
# -------------------------------------------

c.KubeSpawner.namespace = 'odc-system'
c.KubeSpawner.image = 'aub2205926/my-custom-jupyter:1.1'
c.KubeSpawner.image_pull_policy = 'IfNotPresent'

# Ép CONTAINER CHẠY JUPYTER LIÊN TỤC
c.KubeSpawner.cmd = ['jupyterhub-singleuser']
c.KubeSpawner.args = ['--allow-root']

# Truyền tự động biến môi trường ODC vào từng Pod Jupyter con
c.KubeSpawner.environment = {
    'DB_HOSTNAME': 'postgres-svc',
    'DB_PORT': '5432',
    'DB_DATABASE': 'opendatacube',
    'ODC_DEFAULT_INDEX_DRIVER': 'postgis',
    'DATACUBE_INDEX_DRIVER': 'postgis',
    'ODC_DEFAULT_DB_URL': 'postgresql://$(DB_USER):$(DB_PASSWORD)@$(DB_HOSTNAME):$(DB_PORT)/$(DB_DATABASE)',
    'DATACUBE_DB_URL': 'postgresql://$(DB_USER):$(DB_PASSWORD)@$(DB_HOSTNAME):$(DB_PORT)/$(DB_DATABASE)'
}

# Nạp thông tin từ Secret làm biến môi trường
c.KubeSpawner.extra_container_config = {
    "envFrom": [
        {"secretRef": {"name": "odc-secrets"}}
    ]
}

# --- CẤU HÌNH LƯU TRỮ BỀN VỮNG (CHUẨN KUBESPAWNER) ---
c.KubeSpawner.notebook_dir = '/home/jovyan/work'

# Khai báo tên ổ cứng và yêu cầu tạo tự động
c.KubeSpawner.pvc_name_template = 'jupyter-workspace-{username}'
c.KubeSpawner.storage_pvc_ensure = True
c.KubeSpawner.storage_capacity = '2Gi'
c.KubeSpawner.storage_access_modes = ['ReadWriteOnce']

# Định nghĩa Volume tham chiếu tới ổ cứng vừa tạo
c.KubeSpawner.volumes = [
    {
        'name': 'workspace-volume',
        'persistentVolumeClaim': {
            'claimName': 'jupyter-workspace-{username}'
        }
    }
]

# Cắm (Mount) Volume đó vào chính xác thư mục của Jupyter
c.KubeSpawner.volume_mounts = [
    {
        'name': 'workspace-volume',
        'mountPath': '/home/jovyan/work'
    }
]
# -----------------------------------------------------

# --- CẤU HÌNH PHẦN CỨNG MẶC ĐỊNH CHO TẤT CẢ USER ---
c.KubeSpawner.cpu_limit = 1
c.KubeSpawner.cpu_guarantee = 0.5
c.KubeSpawner.mem_limit = '1G'
c.KubeSpawner.mem_guarantee = '1G'
# ---------------------------------------------------