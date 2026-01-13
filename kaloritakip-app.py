import React, { useState } from 'react';
import { Trash2, Plus } from 'lucide-react';

export default function CalorieTracker() {
  const [meals, setMeals] = useState({
    'Kahvaltı': [],
    'Öğle Yemeği': [],
    'Akşam Yemeği': [],
    'Ara Öğün': []
  });
  const [foodName, setFoodName] = useState('');
  const [amount, setAmount] = useState('');
  const [unit, setUnit] = useState('g');
  const [selectedMeal, setSelectedMeal] = useState('Kahvaltı');
  const [dailyGoal, setDailyGoal] = useState(2000);
  const [showGoalInput, setShowGoalInput] = useState(false);
  const [goalInput, setGoalInput] = useState(dailyGoal);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Yiyecek kalori ve makrobesin değerleri (per 100g)
  // Format: [kalori, protein%, karbonhidrat%, yağ%]
  const foodDatabase = {
    'tavuk haşlama': [165, 31, 0, 3.6],
    'tavuk ızgara': [165, 31, 0, 3.6],
    'tavuk': [165, 31, 0, 3.6],
    'kızarmış tavuk': [220, 26, 0, 12],
    'siyah fasulye': [132, 9, 24, 0.5],
    'beyaz fasulye': [88, 7, 16, 0.3],
    'mercimek': [116, 9, 20, 0.4],
    'kırmızı mercimek': [131, 12, 23, 0.4],
    'pirinç': [130, 2.7, 28, 0.3],
    'kahverengi pirinç': [112, 2.6, 24, 0.9],
    'pasta': [131, 5, 25, 1.1],
    'ekmek': [265, 9, 49, 3.3],
    'beyaz ekmek': [265, 9, 49, 3.3],
    'tam buğday ekmek': [246, 13, 41, 3.7],
    'muz': [89, 1.1, 23, 0.3],
    'elma': [52, 0.26, 14, 0.17],
    'portakal': [47, 0.9, 12, 0.12],
    'karpuz': [30, 0.6, 8, 0.2],
    'çilek': [32, 0.7, 8, 0.3],
    'blueberry': [57, 0.7, 14, 0.3],
    'üzüm': [67, 0.7, 17, 0.2],
    'yer fıstığı': [567, 26, 16, 49],
    'yumurta': [155, 13, 1.1, 11],
    'beyaz peynir': [112, 18, 3.5, 4],
    'cheddar peynir': [403, 23, 1.3, 33],
    'süt': [61, 3.2, 4.8, 3.3],
    'yoğurt': [59, 3.5, 3.3, 0.4],
    'balık': [82, 18, 0, 0.7],
    'somon': [208, 20, 0, 13],
    'sardalya': [208, 25, 0, 11],
    'et': [250, 26, 0, 15],
    'kırmızı et': [250, 26, 0, 15],
    'domuz eti': [242, 27, 0, 14],
    'keçi eti': [143, 23, 0, 4.5],
    'patates': [77, 2, 17, 0.1],
    'tatlı patates': [86, 1.6, 20, 0.1],
    'brokoli': [34, 2.8, 7, 0.4],
    'karnabahar': [25, 1.9, 5, 0.3],
    'marul': [15, 1.2, 3, 0.2],
    'domates': [18, 0.9, 3.9, 0.2],
    'salata': [20, 1, 4, 0.2],
    'havuç': [41, 0.9, 10, 0.2],
    'soğan': [40, 1.1, 9, 0.1],
    'sarımsak': [149, 6.4, 33, 0.5],
    'zeytinyağı': [884, 0, 0, 100],
    'tereyağ': [717, 0.7, 0.1, 81],
    'bal': [304, 0.3, 82, 0],
    'çikolata': [535, 5, 57, 31],
    'bisküvi': [430, 7, 66, 17],
    'gözleme': [250, 8, 35, 10],
    'pide': [220, 8, 42, 2],
    'pizza': [266, 12, 36, 10],
    'makarna': [371, 12, 75, 1.1],
    'sushi': [140, 3, 20, 0.5],
    'noodle': [138, 3, 25, 2],
    'çorba': [50, 2, 8, 1],
    'ayran': [34, 3.2, 4, 0.4],
    'kola': [42, 0, 11, 0],
    'meyve suyu': [45, 0.5, 11, 0.1],
    'kahve': [2, 0.2, 0, 0],
    'çay': [2, 0.4, 0, 0],
    'sos': [150, 2, 14, 9],
    'mayonez': [680, 0.8, 0.6, 75],
    'bulgur': [342, 12, 75, 1.3],
    'couscous': [376, 13, 77, 1.6],
    'falafel': [333, 13, 32, 17],
    'hummus': [170, 7.9, 14, 9.6],
    'tahini': [630, 17, 21, 54],
    'balık yağı': [902, 0, 0, 100],
    'hindistan cevizi': [354, 3.3, 15, 34]
  };

  const calculateMacros = async (food, amountValue, unitValue) => {
    const foodKey = food.toLowerCase().trim();
    let foodData = null;

    // Tam eşleşme kontrolü
    if (foodDatabase[foodKey]) {
      foodData = foodDatabase[foodKey];
    } else {
      // Kısmi eşleşme kontrolü
      for (const key in foodDatabase) {
        if (foodKey.includes(key) || key.includes(foodKey)) {
          foodData = foodDatabase[key];
          break;
        }
      }
    }

    // Bilinmeyen yiyecek ise API'dan ara
    if (!foodData) {
      try {
        const response = await fetch("https://api.anthropic.com/v1/messages", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            model: "claude-sonnet-4-20250514",
            max_tokens: 1000,
            messages: [
              {
                role: "user",
                content: `"${food}" yiyeceğinin 100 gram başına besin değerlerini JSON formatında döndür. Format: {"calories": sayı, "protein": yüzde, "carbs": yüzde, "fat": yüzde}. Sadece JSON döndür, başka bir şey yazma.`
              }
            ],
          })
        });

        if (!response.ok) {
          throw new Error('API hatası');
        }

        const data = await response.json();
        const jsonText = data.content[0].text.trim();
        const parsed = JSON.parse(jsonText);

        if (!parsed.calories) {
          throw new Error(`"${food}" bulunamadı.`);
        }

        foodData = [parsed.calories, parsed.protein || 0, parsed.carbs || 0, parsed.fat || 0];
      } catch (err) {
        throw new Error(`"${food}" için besin bilgisi bulunamadı.`);
      }
    }

    let grams = parseFloat(amountValue);

    // Birim dönüştürme
    if (unitValue === 'kg') grams *= 1000;
    else if (unitValue === 'porsiyon') grams *= 150;
    else if (unitValue === 'adet') {
      if (foodKey.includes('yumurta')) grams = 50;
      else if (foodKey.includes('muz')) grams = 120;
      else if (foodKey.includes('elma') || foodKey.includes('portakal')) grams = 150;
      else grams = 100;
    }

    const [calories, proteinPercent, carbsPercent, fatPercent] = foodData;
    const totalCalories = (grams / 100) * calories;
    const proteinCalories = totalCalories * (proteinPercent / 100);
    const carbsCalories = totalCalories * (carbsPercent / 100);
    const fatCalories = totalCalories * (fatPercent / 100);

    return {
      calories: Math.round(totalCalories),
      protein: Math.round(proteinCalories),
      carbs: Math.round(carbsCalories),
      fat: Math.round(fatCalories),
      proteinPercent: proteinPercent,
      carbsPercent: carbsPercent,
      fatPercent: fatPercent
    };
  };

  const addFood = async () => {
    if (!foodName.trim() || !amount.trim()) {
      setError('Lütfen yiyecek adı ve miktarını girin');
      return;
    }

    setError('');
    setLoading(true);

    try {
      const macros = await calculateMacros(foodName, amount, unit);
      const newFood = {
        id: Date.now(),
        name: foodName,
        amount: amount,
        unit: unit,
        ...macros
      };

      setMeals({
        ...meals,
        [selectedMeal]: [...meals[selectedMeal], newFood]
      });

      setFoodName('');
      setAmount('');
      setUnit('g');
    } catch (err) {
      setError(err.message);
    }

    setLoading(false);
  };

  const removeFood = (mealName, id) => {
    setMeals({
      ...meals,
      [mealName]: meals[mealName].filter(food => food.id !== id)
    });
  };

  const calculateMealTotals = (mealFoods) => {
    return mealFoods.reduce(
      (acc, food) => ({
        calories: acc.calories + food.calories,
        protein: acc.protein + food.protein,
        carbs: acc.carbs + food.carbs,
        fat: acc.fat + food.fat
      }),
      { calories: 0, protein: 0, carbs: 0, fat: 0 }
    );
  };

  const allFoods = Object.values(meals).flat();
  const totalCalories = allFoods.reduce((sum, food) => sum + food.calories, 0);
  const totalProtein = allFoods.reduce((sum, food) => sum + food.protein, 0);
  const totalCarbs = allFoods.reduce((sum, food) => sum + food.carbs, 0);
  const totalFat = allFoods.reduce((sum, food) => sum + food.fat, 0);

  const remaining = dailyGoal - totalCalories;
  const percentage = (totalCalories / dailyGoal) * 100;

  const updateGoal = () => {
    const newGoal = parseInt(goalInput);
    if (newGoal > 0) {
      setDailyGoal(newGoal);
      setShowGoalInput(false);
    }
  };

  const getProgressColor = () => {
    if (percentage <= 100) return 'bg-green-500';
    if (percentage <= 110) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const MacroBar = ({ protein, carbs, fat, calories }) => {
    if (calories === 0) return null;
    const proteinPercent = (protein / calories) * 100;
    const carbsPercent = (carbs / calories) * 100;
    const fatPercent = (fat / calories) * 100;

    return (
      <div className="flex gap-1 h-3 rounded-full overflow-hidden bg-gray-200">
        {proteinPercent > 0 && <div className="bg-red-500" style={{ width: `${proteinPercent}%` }} />}
        {carbsPercent > 0 && <div className="bg-blue-500" style={{ width: `${carbsPercent}%` }} />}
        {fatPercent > 0 && <div className="bg-yellow-500" style={{ width: `${fatPercent}%` }} />}
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-center text-gray-800 mb-8">Günlük Kalori & Makro Takibi</h1>

        {/* Günlük Özet */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold text-gray-700">Günlük Özet</h2>
            <button
              onClick={() => setShowGoalInput(!showGoalInput)}
              className="text-sm text-indigo-600 hover:text-indigo-700 font-medium"
            >
              Düzenle
            </button>
          </div>

          {showGoalInput ? (
            <div className="flex gap-2 mb-4">
              <input
                type="number"
                value={goalInput}
                onChange={(e) => setGoalInput(e.target.value)}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-indigo-500"
                placeholder="Kalori hedefi"
              />
              <button
                onClick={updateGoal}
                className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
              >
                Kaydet
              </button>
            </div>
          ) : null}

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-indigo-50 p-4 rounded-lg">
              <p className="text-sm text-gray-600">Kalori</p>
              <p className="text-2xl font-bold text-indigo-600">{totalCalories}</p>
              <p className="text-xs text-gray-500">Hedef: {dailyGoal}</p>
            </div>
            <div className="bg-red-50 p-4 rounded-lg">
              <p className="text-sm text-gray-600">Protein</p>
              <p className="text-2xl font-bold text-red-600">{totalProtein}</p>
              <p className="text-xs text-gray-500">{((totalProtein / totalCalories) * 100).toFixed(1)}%</p>
            </div>
            <div className="bg-blue-50 p-4 rounded-lg">
              <p className="text-sm text-gray-600">Karbonhidrat</p>
              <p className="text-2xl font-bold text-blue-600">{totalCarbs}</p>
              <p className="text-xs text-gray-500">{((totalCarbs / totalCalories) * 100).toFixed(1)}%</p>
            </div>
            <div className="bg-yellow-50 p-4 rounded-lg">
              <p className="text-sm text-gray-600">Yağ</p>
              <p className="text-2xl font-bold text-yellow-600">{totalFat}</p>
              <p className="text-xs text-gray-500">{((totalFat / totalCalories) * 100).toFixed(1)}%</p>
            </div>
          </div>

          {/* İlerleme Barı */}
          <div className="space-y-2">
            <div className="flex justify-between text-sm text-gray-600">
              <span>Tüketilen: <strong className="text-gray-800">{totalCalories} kcal</strong></span>
              <span>Kalan: <strong className={remaining >= 0 ? 'text-green-600' : 'text-red-600'}>{remaining} kcal</strong></span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-4 overflow-hidden">
              <div
                className={`h-full ${getProgressColor()} transition-all duration-300`}
                style={{ width: `${Math.min(percentage, 100)}%` }}
              />
            </div>
          </div>
        </div>

        {/* Yiyecek Ekle */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-700 mb-4">Yiyecek Ekle</h2>

          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}

          <div className="space-y-3">
            <select
              value={selectedMeal}
              onChange={(e) => setSelectedMeal(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-indigo-500 bg-white font-medium"
            >
              <option value="Kahvaltı">Kahvaltı</option>
              <option value="Öğle Yemeği">Öğle Yemeği</option>
              <option value="Akşam Yemeği">Akşam Yemeği</option>
              <option value="Ara Öğün">Ara Öğün</option>
            </select>

            <input
              type="text"
              placeholder="Yiyecek adı"
              value={foodName}
              onChange={(e) => setFoodName(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && addFood()}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-indigo-500"
            />

            <div className="flex gap-2">
              <input
                type="number"
                placeholder="Miktar"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && addFood()}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-indigo-500"
              />
              <select
                value={unit}
                onChange={(e) => setUnit(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-indigo-500 bg-white"
              >
                <option value="g">Gram (g)</option>
                <option value="kg">Kilogram (kg)</option>
                <option value="adet">Adet</option>
                <option value="porsiyon">Porsiyon</option>
              </select>
            </div>

            <button
              onClick={addFood}
              disabled={loading}
              className="w-full bg-indigo-600 text-white py-2 rounded-lg hover:bg-indigo-700 font-medium flex items-center justify-center gap-2 disabled:bg-gray-400"
            >
              <Plus size={20} /> {loading ? 'Hesaplanıyor...' : 'Ekle'}
            </button>
          </div>
        </div>

        {/* Öğünler */}
        {Object.entries(meals).map(([mealName, mealFoods]) => {
          const mealTotals = calculateMealTotals(mealFoods);
          return (
            <div key={mealName} className="bg-white rounded-lg shadow-lg p-6 mb-6">
              <h2 className="text-xl font-semibold text-gray-700 mb-4">{mealName}</h2>

              {mealFoods.length === 0 ? (
                <p className="text-center text-gray-500 py-4">Henüz yiyecek eklenmedi</p>
              ) : (
                <>
                  <div className="space-y-3 mb-4">
                    {mealFoods.map((food) => (
                      <div key={food.id} className="p-3 bg-gray-50 rounded-lg">
                        <div className="flex justify-between items-start mb-2">
                          <div>
                            <p className="font-medium text-gray-800">{food.name}</p>
                            <p className="text-sm text-gray-600">{food.amount}{food.unit}</p>
                          </div>
                          <button
                            onClick={() => removeFood(mealName, food.id)}
                            className="text-red-500 hover:text-red-700"
                          >
                            <Trash2 size={18} />
                          </button>
                        </div>

                        <MacroBar
                          protein={food.protein}
                          carbs={food.carbs}
                          fat={food.fat}
                          calories={food.calories}
                        />

                        <div className="flex justify-between text-xs text-gray-600 mt-2">
                          <span>{food.calories} kcal</span>
                          <span>P: {food.proteinPercent.toFixed(1)}%</span>
                          <span>K: {food.carbsPercent.toFixed(1)}%</span>
                          <span>Y: {food.fatPercent.toFixed(1)}%</span>
                        </div>
                      </div>
                    ))}
                  </div>

                  {mealTotals.calories > 0 && (
                    <div className="pt-4 border-t-2 border-gray-200">
                      <div className="flex justify-between items-center mb-2">
                        <span className="font-semibold text-gray-700">Öğün Toplamı</span>
                        <span className="font-bold text-indigo-600">{mealTotals.calories} kcal</span>
                      </div>

                      <MacroBar
                        protein={mealTotals.protein}
                        carbs={mealTotals.carbs}
                        fat={mealTotals.fat}
                        calories={mealTotals.calories}
                      />

                      <div className="flex justify-between text-sm text-gray-700 mt-2 font-medium">
                        <span>P: {((mealTotals.protein / mealTotals.calories) * 100).toFixed(1)}%</span>
                        <span>K: {((mealTotals.carbs / mealTotals.calories) * 100).toFixed(1)}%</span>
                        <span>Y: {((mealTotals.fat / mealTotals.calories) * 100).toFixed(1)}%</span>
                      </div>
                    </div>
                  )}
                </>
              )}
            </div>
          );
        })}

        {/* Renk Açıklaması */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="font-semibold text-gray-700 mb-3">Makro Oranları</h3>
          <div className="flex gap-4 text-sm">
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-red-500 rounded"></div>
              <span>Protein</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-blue-500 rounded"></div>
              <span>Karbonhidrat</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-yellow-500 rounded"></div>
              <span>Yağ</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
