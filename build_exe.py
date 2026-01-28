import PyInstaller.__main__

PyInstaller.__main__.run([
    'gui.py',
    '--onefile',
    '--windowed',
    '--name=FantasyGroundsExporter_v4',
    '--add-data=dnd5e_rules.yaml;.'
])
