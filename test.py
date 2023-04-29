from app.main.background import get_competition_info_xml, get_all_results, cleanup_athletes

comp = {
    'id': 9153,
    'source': 'html',
    'domain': 'uitslagen.atletiek.nl'
}

get_competition_info_xml(comp)
get_all_results(comp)
cleanup_athletes(comp)
