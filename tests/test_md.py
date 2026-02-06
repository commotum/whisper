from whisp.md import Segment, segments_to_turns, render_markdown


def test_segments_to_turns_gap_split():
    segs = [
        Segment(0.0, 1.0, "hello"),
        Segment(1.1, 2.0, "world"),
        Segment(5.0, 6.0, "new turn"),
    ]
    turns = segments_to_turns(segs, max_gap_s=1.2)
    assert len(turns) == 2


def test_render_markdown_basic():
    turns = [
        Segment(0.0, 1.0, "hello"),
    ]
    t = segments_to_turns(turns, max_gap_s=1.2)
    md = render_markdown(title="T", speaker="S", turns=t)
    assert md.startswith("# T")
    assert "**S (00:00:00):**" in md
