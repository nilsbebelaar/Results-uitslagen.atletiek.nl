from app.main.background import get_competition_info_xml, get_all_results, cleanup_athletes, save_to_file

comp = {
    'id': 9396,
    'source': 'html',
    'domain': 'uitslagen.atletiek.nl'
}

get_competition_info_xml(comp)
get_all_results(comp)
cleanup_athletes(comp)
save_to_file(comp)