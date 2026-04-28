from app.services.filtering import should_review_file


def test_should_skip_binary_file():
    assert not should_review_file('image.png', 'modified', 'patch')


def test_should_skip_removed_file():
    assert not should_review_file('main.py', 'removed', 'patch')


def test_should_review_code_file():
    assert should_review_file('app/main.py', 'modified', '@@ -1 +1 @@')
