'''
This is the following file (on average household size), expressed as a function:

https://population.un.org/household/exceldata/population_division_UN_Houseshold_Size_and_Composition_2019.xlsx
'''

data = {
    'Afghanistan': 8.036,
    'Albania': 3.299,
    'Angola': 4.815,
    'Argentina': 3.258,
    'Armenia': 3.542,
    'Aruba': 2.889,
    'Australia': 2.546,
    'Austria': 2.271,
    'Azerbaijan': 4.548,
    'Bahamas': 3.395,
    'Bangladesh': 4.469,
    'Belarus': 2.482,
    'Belgium': 2.362,
    'Benin': 5.186,
    'Bermuda': 2.262,
    'Bolivia (Plurinational State of)': 3.530,
    'Botswana': 3.524,
    'Brazil': 3.311,
    'Bulgaria': 2.337,
    'Burkina Faso': 5.924,
    'Burundi': 4.830,
    'Cambodia': 4.611,
    'Cameroon': 4.992,
    'Canada': 2.448,
    'Central African Republic': 4.906,
    'Chad': 5.777,
    'Chile': 3.576,
    'China': 3.384,
    'China, Hong Kong SAR': 2.834,
    'China, Macao SAR': 3.066,
    'Colombia': 3.526,
    'Comoros': 5.371,
    'Congo': 4.307,
    'Costa Rica': 3.461,
    'Croatia': 2.795,
    'Cuba': 3.136,
    'Cyprus': 2.747,
    'Czechia': 2.395,
    "Côte d'Ivoire": 5.090,
    "Dem. People's Rep. of Korea": 3.929,
    'Dem. Republic of the Congo': 5.302,
    'Dominican Republic': 3.477,
    'Ecuador': 3.779,
    'Egypt': 4.130,
    'El Salvelop07': 4.069,
    'Estonia': 2.297,
    'Ethiopia': 4.614,
    'Fiji': 4.572,
    'Finland': 2.074,
    'France': 2.222,
    'French Guiana': 3.454,
    'Gabon': 4.097,
    'Gambia': 8.229,
    'Georgia': 3.337,
    'Germany': 2.046,
    'Ghana': 3.492,
    'Greece': 2.440,
    'Guadeloupe': 2.296,
    'Guatemala': 4.805,
    'Guinea': 6.250,
    'Guyana': 3.795,
    'Haiti': 4.293,
    'Honduras': 4.467,
    'Hungary': 2.603,
    'India': 4.572,
    'Indonesia': 3.859,
    'Iran (Islamic Republic of)': 3.492,
    'Iraq': 7.703,
    'Ireland': 2.766,
    'Isle of Man': 2.283,
    'Israel': 3.141,
    'Italy': 2.399,
    'Jamaica': 3.060,
    'Japan': 2.330,
    'Jordan': 4.718,
    'Kazakhstan': 3.496,
    'Kenya': 3.638,
    'Kyrgyzstan': 4.214,
    "Lao People's Dem. Republic": 5.765,
    'Latvia': 2.578,
    'Lesotho': 3.344,
    'Liberia': 4.945,
    'Liechtenstein': 2.320,
    'Lithuania': 2.320,
    'Luxembourg': 2.412,
    'Madagascar': 4.949,
    'Malawi': 4.508,
    'Malaysia': 4.557,
    'Maldives': 5.399,
    'Mali': 5.811,
    'Malta': 2.852,
    'Martinique': 2.248,
    'Mauritius': 3.475,
    'Mayotte': 4.102,
    'Mexico': 3.740,
    'Mongolia': 4.321,
    'Montenegro': 3.214,
    'Morocco': 5.236,
    'Mozambique': 4.366,
    'Myanmar': 4.223,
    'Namibia': 4.238,
    'Nepal': 4.239,
    'Netherlands': 2.226,
    'New Zealand': 2.672,
    'Nicaragua': 4.919,
    'Niger': 5.916,
    'Nigeria': 4.901,
    'Norway': 2.215,
    'Oman': 8.017,
    'Pakistan': 6.804,
    'Panama': 3.670,
    'Papua New Guinea': 5.430,
    'Paraguay': 4.632,
    'Peru': 3.752,
    'Philippines': 4.226,
    'Poland': 2.806,
    'Portugal': 2.655,
    'Puerto Rico': 2.670,
    'Republic of Korea': 2.529,
    'Republic of Moldova': 2.888,
    'Romania': 2.879,
    'Russian Federation': 2.584,
    'Rwanda': 4.259,
    'Réunion': 2.643,
    'Saint-Barthélemy': 2.424,
    'Saint-Martin (French part)': 2.564,
    'Samoa': 6.751,
    'Sao Tome and Principe': 3.836,
    'Senegal': 8.661,
    'Serbia': 2.879,
    'Seychelles': 3.778,
    'Sierra Leone': 5.899,
    'Singapore': 3.291,
    'Sint Maarten (Dutch part)': 2.579,
    'Slovakia': 2.801,
    'Slovenia': 2.467,
    'South Africa': 3.362,
    'South Sudan': 5.947,
    'Spain': 2.694,
    'State of Palestine': 5.476,
    'Sudan': 5.590,
    'Suriname': 3.940,
    'Swaziland': 4.737,
    'Switzerland': 2.212,
    'Tajikistan': 5.993,
    'Thailand': 3.693,
    'Timor-Leste': 5.267,
    'Togo': 4.551,
    'Tokelau': 5.243,
    'Trinidad and Tobago': 3.290,
    'Turkey': 4.071,
    'Uganda': 4.534,
    'Ukraine': 2.458,
    'United Kingdom': 2.265,
    'United Republic of Tanzania': 4.851,
    'United States of America': 2.491,
    'Uruguay': 2.781,
    'Uzbekistan': 5.242,
    'Venezuela (Bolivarian Republic of)': 4.331,
    'Viet Nam': 3.783,
    'Yemen': 6.672,
    'Zambia': 5.130,
    'Zimbabwe': 4.077,
    'Bolivia': 3.530,
    'Burkina': 5.924,
    'Iran': 3.492,
    'Korea': 2.529,
    'South Korea': 2.529,
    'Moldova': 2.888,
    'Russia': 2.584,
    'Palestine': 5.476,
    'Tanzania': 4.851,
    'USA': 2.491,
    'United States': 2.491,
    'Venezuela': 4.331,
    'Vietnam': 3.783,
}
