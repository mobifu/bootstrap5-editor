import pytest

from models import (
    AccordionBlock,
    AlertBlock,
    BadgeBlock,
    ButtonBlock,
    CardBlock,
    Column,
    Element,
    FormInputBlock,
    HtmlBlock,
    ImageBlock,
    ListGroupBlock,
    NavbarBlock,
    Page,
    Row,
    TableBlock,
    TextBlock,
    _sanitize_css_class,
    _sanitize_url,
)


def test_element_base_and_spacing():
    elem = Element(margin_top="3", padding_bottom="2")
    assert elem.get_spacing_classes() == "mt-3 pb-2"
    assert elem.apply_spacing_to_html("<p>Hi</p>") == '<div class="mt-3 pb-2">\n<p>Hi</p>\n</div>'

    with pytest.raises(NotImplementedError):
        elem.render()

    d = elem.to_dict()
    assert d["margin_top"] == "3"
    assert d["padding_bottom"] == "2"


def test_element_spacing_render_in_column():
    tb = TextBlock(
        text="Hallo Welt",
        margin_top="4",
        margin_bottom="2",
        padding_top="1",
        padding_bottom="3",
    )
    col = Column(span=12)
    col.add_element(tb)

    rendered = col.render(version="5")
    assert 'class="mt-4 mb-2 pt-1 pb-3"' in rendered
    assert "<p>Hallo Welt</p>" in rendered

    # Abstands-Serialisierung & Deserialisierung
    col_dict = col.to_dict()
    restored_col = Element.from_dict(col_dict)
    restored_tb = restored_col.elements[0]
    assert restored_tb.margin_top == "4"
    assert restored_tb.margin_bottom == "2"
    assert restored_tb.padding_top == "1"
    assert restored_tb.padding_bottom == "3"


def test_text_block():
    tb = TextBlock(text="Hello World", tag="h2")
    rendered = tb.render()
    assert "<h2>Hello World</h2>" in rendered

    tb_dict = tb.to_dict()
    tb_restored = Element.from_dict(tb_dict)
    assert isinstance(tb_restored, TextBlock)
    assert tb_restored.text == "Hello World"
    assert tb_restored.tag == "h2"


def test_image_block():
    img = ImageBlock(url="test.png", alt="Test")
    rendered = img.render()
    assert 'src="test.png"' in rendered
    assert 'alt="Test"' in rendered

    restored = Element.from_dict(img.to_dict())
    assert isinstance(restored, ImageBlock)
    assert restored.url == "test.png"


def test_button_block():
    btn = ButtonBlock(text="Click", url="https://example.com", style="danger")
    rendered = btn.render()
    assert 'href="https://example.com"' in rendered
    assert "btn-danger" in rendered

    restored = Element.from_dict(btn.to_dict())
    assert restored.style == "danger"


def test_alert_block():
    alert = AlertBlock(text="Warning!", style="warning")
    rendered = alert.render()
    assert "alert-warning" in rendered

    restored = Element.from_dict(alert.to_dict())
    assert restored.style == "warning"


def test_card_block():
    card = CardBlock(title="Card Title", content="Card body text")
    rendered = card.render()
    assert "Card Title" in rendered
    assert "Card body text" in rendered

    restored = Element.from_dict(card.to_dict())
    assert restored.title == "Card Title"


def test_badge_block():
    badge = BadgeBlock(text="New", style="success")
    rendered = badge.render()
    assert "bg-success" in rendered

    restored = Element.from_dict(badge.to_dict())
    assert restored.text == "New"


def test_accordion_block():
    acc = AccordionBlock(items=[{"title": "Section 1", "content": "Body 1"}])
    rendered = acc.render()
    assert "Section 1" in rendered
    assert "Body 1" in rendered

    restored = Element.from_dict(acc.to_dict())
    assert len(restored.items) == 1


def test_list_group_block():
    lg = ListGroupBlock(items=["Item A", "Item B"])
    rendered = lg.render()
    assert '<li class="list-group-item">Item A</li>' in rendered

    restored = Element.from_dict(lg.to_dict())
    assert restored.items == ["Item A", "Item B"]


def test_table_block():
    tbl = TableBlock(headers=["A", "B"], rows=[["1", "2"], ["3", "4"]], striped=True)
    rendered = tbl.render()
    assert "table-striped" in rendered
    assert "<th>A</th>" in rendered

    restored = Element.from_dict(tbl.to_dict())
    assert restored.headers == ["A", "B"]


def test_html_block():
    hb = HtmlBlock(code="<div>Custom</div>")
    assert hb.render() == "<div>Custom</div>"

    restored = Element.from_dict(hb.to_dict())
    assert restored.code == "<div>Custom</div>"


def test_form_input_block():
    fi = FormInputBlock(
        label="E-Mail",
        input_type="email",
        placeholder="name@example.com",
        help_text="Deine Adresse",
    )
    rendered = fi.render()
    assert 'type="email"' in rendered
    assert "E-Mail" in rendered
    assert "name@example.com" in rendered
    assert "Deine Adresse" in rendered

    restored = Element.from_dict(fi.to_dict())
    assert restored.label == "E-Mail"
    assert restored.input_type == "email"


def test_navbar_block():
    nav = NavbarBlock(brand="MyBrand", bg_style="dark")
    rendered = nav.render()
    assert "MyBrand" in rendered
    assert "bg-dark" in rendered

    restored = Element.from_dict(nav.to_dict())
    assert restored.brand == "MyBrand"
    assert restored.bg_style == "dark"


def test_column_row_page_hierarchy_and_reordering():
    page = Page(title="Test Page")
    row1 = Row()
    row2 = Row()
    col1 = Column(span=6)
    col2 = Column(span=6)

    tb1 = TextBlock(text="First")
    tb2 = TextBlock(text="Second")

    col1.add_element(tb1)
    col1.add_element(tb2)
    row1.add_column(col1)
    row1.add_column(col2)
    page.add_row(row1)
    page.add_row(row2)

    # Reordering in Column
    col1.move_element_down(tb1.id)
    assert col1.elements[0].id == tb2.id

    col1.move_element_up(tb1.id)
    assert col1.elements[0].id == tb1.id

    # Reordering in Page
    page.move_row_down(row1.id)
    assert page.rows[0].id == row2.id

    page.move_row_up(row1.id)
    assert page.rows[0].id == row1.id

    # Removal
    col1.remove_element(tb2.id)
    assert len(col1.elements) == 1

    row1.remove_column(col2.id)
    assert len(row1.columns) == 1

    page.remove_row(row2.id)
    assert len(page.rows) == 1

    # Serialization
    p_dict = page.to_dict()
    restored_page = Element.from_dict(p_dict)
    assert restored_page.title == "Test Page"
    assert len(restored_page.rows) == 1


def test_unknown_element_type():
    with pytest.raises(ValueError, match="Unbekannter Element-Typ: InvalidType"):
        Element.from_dict({"type": "InvalidType"})


def test_url_sanitization_xss_prevention():
    dangerous_urls = [
        "javascript:alert(1)",
        "JAVASCRIPT:console.log('xss')",
        "vbscript:msgbox(1)",
        "data:text/html,<script>alert(1)</script>",
    ]
    for url in dangerous_urls:
        btn = ButtonBlock(text="Klick mich", url=url)
        rendered = btn.render()
        assert 'href="javascript:' not in rendered.lower()
        assert 'href="data:' not in rendered.lower()
        assert 'href="#"' in rendered

        nav = NavbarBlock(brand="Nav", links=[{"text": "Evil", "url": url}])
        nav_rendered = nav.render()
        assert 'href="javascript:' not in nav_rendered.lower()
        assert 'href="#"' in nav_rendered


def test_url_sanitization_valid_urls():
    valid_urls = [
        "https://example.com/test?a=1&b=2",
        "http://localhost:8080",
        "#section1",
        "/about-us",
        "./relative/path.html",
        "mailto:info@example.com",
        "tel:+4912345678",
    ]
    for url in valid_urls:
        btn = ButtonBlock(text="Klick", url=url)
        rendered = btn.render()
        assert "href=" in rendered
        assert _sanitize_url(url, fallback="#") in rendered


def test_css_class_attribute_injection():
    malicious_style = 'primary" onclick="alert(1)" style="color:red'
    sanitized = _sanitize_css_class(malicious_style, fallback="primary")
    assert '"' not in sanitized
    assert " " not in sanitized
    assert "=" not in sanitized
    assert ";" not in sanitized
