# build.sh
# Descargar el paquete .deb del driver
curl -O https://packages.microsoft.com/ubuntu/20.04/prod/pool/main/m/msodbcsql18/msodbcsql18_18.3.2.1-1_amd64.deb

# Instalar localmente sin privilegios root
dpkg -x msodbcsql18_18.3.2.1-1_amd64.deb ~/.local/

# Configurar variables de entorno
echo 'export LD_LIBRARY_PATH=~/.local/opt/microsoft/msodbcsql18/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
echo 'export PATH=~/.local/opt/microsoft/msodbcsql18/bin:$PATH' >> ~/.bashrc
source ~/.bashrc