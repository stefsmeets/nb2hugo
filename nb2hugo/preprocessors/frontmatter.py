from nbconvert.preprocessors import Preprocessor
from nbformat import notebooknode
import warnings


class FrontMatterPreprocessor(Preprocessor):
    """Preprocess the notebook front matter:
    - all the raw cells before a <!--eofm--> divider
    will be considered as part of the front matter and transformed 
    into a unique cell containing a toml front matter
    - all raw cells or code cells before the <!--eofm--> divider will
    be removed
    - all cells after the <!--eofm--> divider will be kept as is.
    """
    
    def preprocess(self, nb, resources):
        """Execute the preprocessing of the notebook."""
        frontmatter, content_cells = self._split_frontmatter(nb)   
        nb.cells = []
        if frontmatter:
            toml_fm = self._toml_frontmatter(frontmatter)
            nb.cells.append(self._raw_cell(toml_fm))
        nb.cells += content_cells
        return nb, resources
    
    def _split_frontmatter(self, nb):
        """Return a pair whose first element is a string containing
        the frontmatter and whose second element is a list of all the
        content cells."""
        frontmatter = ''
        for index, cell in enumerate(nb.cells):
            if cell.cell_type == "raw":
                split = cell.source.split('<!--eofm-->', 1)
                if len(split) > 1: # eofm divider is in the cell
                    fm_part, content_part = split
                    frontmatter += fm_part
                    if content_part.strip():
                        first_content_cell = [self._raw_cell(content_part)]
                    else: 
                        first_content_cell = []
                    return frontmatter, first_content_cell+nb.cells[index + 1:]
                else:
                    return '', nb.cells

        warnings.warn('Notebook does not have a front matter.')
        return '', nb.cells
  
    def _toml_frontmatter(self, nb_fm):
        """Pass notebook toml front matter as is.
        Only the toml delimiter are added.
        """
        return '+++\n' + nb_fm + '\n+++\n'
    
    def _raw_cell(self, source):
        """Create a raw cell with source content."""
        return notebooknode.from_dict({"cell_type": "raw",
                                       "metadata": {},
                                       "source": source})
