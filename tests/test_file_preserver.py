from utils.file_preserver import FilePreserver, PreservedFile
import uuid

def test_PreservedFile_rich_comparisons():
    pf1 = PreservedFile('MemberData.json')
    pf2 = PreservedFile('MemberData.json')
    assert pf1 == pf2
    assert pf1 <= pf2
    assert pf1 >= pf2
    assert not pf1 < pf2
    assert not pf1 > pf2
    assert not pf1 != pf2
    assert hash(pf1) == hash(pf2)

def test_PreservedFile_preserve_then_restore(tmp_path):
    # Prepare a test file.
    pf1 = tmp_path / 'MemberData.json'
    pf1.write_text('Whatever, dude!')
    # Determine what the file's name will be while preserved.
    prefix = uuid.uuid4().hex + '-'
    pf2 = tmp_path / (prefix + 'MemberData.json')
    # Time to test.
    pf3 = PreservedFile(pf1)
    # Restore before preserve is ignored.
    pf3.restore_it()
    pf3.restore_it()
    pf3.preserve_it(prefix)
    # Double preserve is ignored.
    pf3.preserve_it(prefix)
    assert pf2.exists()
    assert not pf1.exists()
    assert pf2.read_text() == 'Whatever, dude!'
    pf3.restore_it()
    assert not pf2.exists()
    assert pf1.exists()

def test_FilePreserver(tmp_path):
    pf1 = tmp_path / 'MemberData.json'
    pf1.write_text('Whatever, dude!')
    with FilePreserver(pf1):
        assert not pf1.exists()
    assert pf1.exists()
    assert pf1.read_text() == 'Whatever, dude!'
    with FilePreserver(str(pf1)):
        assert not pf1.exists()
    assert pf1.exists()
    assert pf1.read_text() == 'Whatever, dude!'
    fp1 = FilePreserver()
    fp1.preserve_this(pf1)
    fp1.preserve_this(str(pf1))
    assert len(fp1._preserve_these) == 1
    with fp1:
        assert not pf1.exists()
    assert pf1.exists()
    assert pf1.read_text() == 'Whatever, dude!'
    fp1 = FilePreserver()
    fp1 += pf1
    fp1 += pf1
    assert len(fp1._preserve_these) == 1
    with fp1:
        assert not pf1.exists()
    assert pf1.exists()
    assert pf1.read_text() == 'Whatever, dude!'
    fp1 = FilePreserver(tmp_path/'MemberData.json', tmp_path/'MemberData.json')
    assert len(fp1._preserve_these) == 1
    with fp1:
        assert not pf1.exists()
    assert pf1.exists()
    assert pf1.read_text() == 'Whatever, dude!'
    pf2 = tmp_path / 'MemberData.json.bak'
    assert not pf2.exists()
    fp1 = FilePreserver(tmp_path/'MemberData.json', tmp_path/'MemberData.json.bak')
    with fp1:
        assert not pf1.exists()
        assert not pf2.exists()
    assert pf1.exists()
    assert not pf2.exists()
