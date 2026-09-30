from biosignal.sources import WHO_GLASS_AMR_ENDPOINT, who_glass_amr_url


def test_who_glass_url_is_reproducible():
    url = who_glass_amr_url(
        columns=["DIM_GEO_CODE_M49", "IND_CODE", "VALUE_NUMERIC"],
        top=5,
    )
    assert url.startswith(WHO_GLASS_AMR_ENDPOINT)
    assert "$select" in url
    assert "$top" in url
    assert "$format" in url
