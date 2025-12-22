import os
import glob

def cleanup_models(directory, keep=20):
    files = glob.glob(os.path.join(directory, "best_gen_*.pkl"))
    # Sort by modification time? Or by Gen number in name?
    # Gen number is consistent.
    
    # helper
    def get_gen(fname):
        try:
            base = os.path.basename(fname)
            # best_gen_123.pkl
            num = base.split('_')[2].split('.')[0]
            return int(num)
        except:
            return -1

    files.sort(key=get_gen)
    
    if len(files) > keep:
        to_delete = files[:-keep]
        for f in to_delete:
            try:
                os.remove(f)
                print(f"Deleted old model: {os.path.basename(f)}")
            except Exception as e:
                print(f"Error deleting {f}: {e}")

if __name__ == "__main__":
    d = os.path.join(os.path.dirname(__file__), 'saved_models')
    cleanup_models(d)
