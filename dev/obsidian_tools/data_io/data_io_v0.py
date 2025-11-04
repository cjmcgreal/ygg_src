import os
import yaml
import pandas as pd
from pathlib import Path

class DataIO:
    def __init__(self, obsidian_path: str):
        """
        Initializes the DataIO class for a given Obsidian vault path.
        
        Args:
            obsidian_path (str): Path to the folder containing markdown notes.
        """
        self.obsidian_path = Path(obsidian_path)

    def read_obsidian_to_df(self) -> pd.DataFrame:
        """
        Reads markdown files with YAML frontmatter and returns a DataFrame.
        
        Returns:
            pd.DataFrame: A DataFrame with one row per note and all frontmatter fields as columns.
        """
        rows = []
        for md_file in self.obsidian_path.glob("*.md"):
            with open(md_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            # Detect frontmatter
            if lines[0].strip() == "---":
                try:
                    end_idx = lines[1:].index("---\n") + 1
                except ValueError:
                    continue  # Skip invalid frontmatter

                frontmatter = yaml.safe_load("".join(lines[1:end_idx]))
                content = "".join(lines[end_idx+1:]).strip()
                row = frontmatter or {}
                row["note_body"] = content
                row["filename"] = md_file.stem
                rows.append(row)
        
        return pd.DataFrame(rows)

    def write_df_to_obsidian(self, df: pd.DataFrame, filename_col="filename") -> None:
        """
        Writes DataFrame rows back into markdown files with YAML frontmatter.
        
        Args:
            df (pd.DataFrame): DataFrame to write.
            filename_col (str): Name of the column containing the output filename.
        """
        for _, row in df.iterrows():
            note_data = row.to_dict()
            filename = note_data.pop(filename_col, "untitled")
            note_body = note_data.pop("note_body", "")
            
            frontmatter = yaml.dump(note_data, sort_keys=False)
            md_text = f"---\n{frontmatter}---\n\n{note_body}"
            
            out_path = self.obsidian_path / f"{filename}.md"
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(md_text)
