import re

def latent_representation_to_fasta(latent_representation, length):
    sequences = [latent_representation[i:i+length] for i in range(0, len(latent_representation), length)]
    fast_str = ""
    fast_str += "> oligo\n"
    fast_str += "\n> oligo\n".join(sequences)
    return fast_str

def get_value_from_fasta(key, fasta_str):
    values = re.findall(f">\s*{key}\s*\n([ACGT]+)\n", fasta_str)
    return values[0] if len(values) == 1 else values

def to_fastq(x):
    fasta = latent_representation_to_fasta(x, 200)
    with open(f"/Users/lukasecilmis/Desktop/parrots.fasta", "w+") as fd:
        fd.write(fasta)

def main():
    with open("/PATH/DNAfile, "r") as fd:
        x = fd.read()
    to_fastq(x)

if __name__ == "__main__":
    main()