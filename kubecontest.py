import epsagon

epsagon.init(
    token='EPSAGON_API_KEY',
    app_name='kubecontest.py',
    metadata_only=False,  # Optional, send more trace data
)

@epsagon.python_wrapper
def main():
    return 'It worked!'

main()