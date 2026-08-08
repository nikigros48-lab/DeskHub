def city_context(request):
    city_data = request.session.get("selected_city_data")
    if city_data:
        return {
            'selected_city': city_data,
            'selected_city_name': city_data.get('name'),
        }
    return {
        'selected_city': None,
        'selected_city_name': None,
    }