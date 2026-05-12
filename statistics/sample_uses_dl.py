import base64
import gzip
import sqlite3

import click
import pandas as pd


def compress_string(text):
    """Compresses a string using GZIP and encodes it in Base64."""
    if not text:
        return ""
    # Convert string to bytes, compress, then encode to base64 string
    content = text.encode("utf-8")
    compressed = gzip.compress(content)
    return base64.b64encode(compressed).decode("utf-8")


@click.command()
@click.argument("db_path", type=click.Path(exists=True))
@click.option("--table", default="markdown", help="Name of the table.")
@click.option("--fraction", default=0.2, help="Fraction to sample (0.0 - 1.0).")
@click.option("--output", default="compressed_sample.csv", help="Output filename.")
def sample_and_compress(db_path, table, fraction, output):
    """Samples a SQLite table and GZIP compresses the 'markdown' column."""

    try:
        conn = sqlite3.connect(db_path)

        click.echo(f"Loading data from {table}...")
        # We only pull the 'markdown' column to save memory, or use SELECT *
        df = pd.read_sql_query(f"SELECT * FROM {table}", conn)

        if "markdown" not in df.columns:
            click.secho("Error: Column 'markdown' not found in table.", fg="red")
            return

        # 1. Random Sample
        df_sample = df.sample(frac=fraction, random_state=42).copy()
        click.echo(f"Sampled {len(df_sample)} rows. Compressing...")

        # 2. Apply GZIP compression to the markdown column
        # Using a progress bar from Click because compression can take a moment
        with click.progressbar(df_sample["markdown"]) as bar:
            df_sample["markdown"] = [compress_string(text) for text in bar]

        # 3. Save to CSV
        df_sample["uses_dl"] = ""
        df_sample.to_csv(output, index=False)
        click.secho(f"Saved compressed sample to {output}", fg="green")

    except Exception as e:
        click.secho(f"An error occurred: {e}", fg="red")
    finally:
        conn.close()


if __name__ == "__main__":
    sample_and_compress()
