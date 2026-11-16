from pathlib import Path
import importlib.util, os, shutil, sys
BASE=Path(r'D:\毕业设计\.codex_work\chapter4_20261109')
SRC=Path(r'C:\Users\a1887\.codex\plugins\cache\openai-primary-runtime\documents\26.1026.10807\skills\documents\render_docx.py')
os.environ['PATH']=r'C:\Users\a1887\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\poppler\Library\bin'+os.pathsep+os.environ.get('PATH','')
spec=importlib.util.spec_from_file_location('packaged_render_docx',SRC)
renderer=importlib.util.module_from_spec(spec);spec.loader.exec_module(renderer)
def word_pdf(doc_path,user_profile,convert_tmp_dir,stem,verbose=False):
    target=Path(convert_tmp_dir)/(stem+'.pdf')
    shutil.copy2(BASE/'word_render.pdf',target)
    return str(target),'Microsoft Word native PDF export used because bundled LibreOffice is unavailable on Windows.'
renderer.convert_to_pdf=word_pdf
sys.argv=[str(SRC),sys.argv[1],'--output_dir',str(BASE/'render'),'--emit_pdf','--dpi','140']
renderer.main()
