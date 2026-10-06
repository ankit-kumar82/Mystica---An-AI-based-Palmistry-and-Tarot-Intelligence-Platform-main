import { NextResponse } from 'next/server';
import { runAIFallback } from '@/lib/ai-fallback';
import { unstable_cache } from 'next/cache';

export async function GET(request: Request) {
  const authHeader = request.headers.get('authorization');
  if (!authHeader) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });

  try {
    const backendUrl = process.env.BACKEND_URL || 'https://mystica-backend.onrender.com';
    const res = await fetch(`${backendUrl}/api/dashboard`, {
      headers: { 'Authorization': authHeader }
    });

    if (!res.ok) throw new Error(`Backend returned ${res.status}`);
    const data = await res.json();
    const todayStr = new Date().toISOString().split('T')[0];

    // =====================================================================
    // 1. SEEKER (USER) AI GENERATION
    // =====================================================================
    if (data.dashboard && data.dashboard.role === 'user') {
      const { userId, aiContext, astrology } = data.dashboard;
      
      const defaultUserData = {
        overview: `The celestial transits today favor conscious introspection for ${aiContext?.sign || 'your sign'}.`,
        career: "Steady momentum surrounds strategic tasks. Keep goals clear.",
        love: "Empathy and mutual respect create deep, nourishing bonds today.",
        health: "Maintain balanced hydration and take brief moments for mindful pause.",
        remedy: "Practice 5 minutes of mindful breathwork before major tasks.",
        luckyColor: "Royal Indigo",
        auspiciousTime: "11:00 AM - 12:30 PM",
        mantra: "Om Gam Ganapataye Namaha",
        lunarPhase: "Waxing Crescent. Ideal for setting intentions."
      };

      // Vercel Global Cache: Locks the AI generation in for 24 hours per user
      const getCachedUserForecast = unstable_cache(
        async () => {
          const prompt = `You are a master astrologer. Provide a daily forecast.
User's Zodiac Sign: ${aiContext?.sign || 'Unknown'}
User's Goal: ${aiContext?.primaryGoal || 'Balance'}
Context: ${aiContext?.readingSummary || 'Seeking guidance'}

Return ONLY a valid JSON object with EXACTLY these keys:
{
    "overview": "2 sentences of general spiritual advice.",
    "career": "1 sentence on career/karma.",
    "love": "1 sentence on love/relationships.",
    "health": "1 sentence on health/vitality.",
    "remedy": "1 practical spiritual action or remedy.",
    "luckyColor": "e.g. Crimson & Gold",
    "auspiciousTime": "e.g. 10:15 AM - 11:45 AM",
    "mantra": "A relevant short mantra",
    "lunarPhase": "e.g., Waxing Crescent. Ideal for setting intentions."
}`;
          try {
            const rawResponse = await runAIFallback({ prompt, fallbackTemplate: JSON.stringify(defaultUserData) });
            return JSON.parse(rawResponse.replace(/```json/g, '').replace(/```/g, '').trim());
          } catch (err) {
            console.error("Dashboard User AI parsing error:", err);
            return defaultUserData;
          }
        },
        [`dashboard-user-${userId}-${todayStr}`],
        { revalidate: 86400 } // 86400 seconds = 24 hours
      );

      const geminiData = await getCachedUserForecast();
      data.dashboard.astrology = { ...astrology, ...geminiData };
      delete data.dashboard.aiContext;
      delete data.dashboard.userId;
    } 
    
    // =====================================================================
    // 2. SPECIALIST AI GENERATION
    // =====================================================================
    else if (data.dashboard && data.dashboard.specialistStats) {
      const role = data.dashboard.role;
      const defaultSpecialistData = {
        message: "Today's planetary currents favor deep discernment and clarity. Anchor your intuition in constructive, empowering remedies.",
        channel: "High Sensitivity",
        crystal: "Grounding Quartz",
        chakra: "Third Eye"
      };

      const getCachedSpecialistForecast = unstable_cache(
        async () => {
          const prompt = `You are a mentor to spiritual practitioners. Provide a daily cosmic alignment forecast for a ${role}.
Return ONLY a valid JSON object with EXACTLY these keys:
{
    "message": "2 sentences of daily guidance advising the practitioner on how to handle client readings today.",
    "channel": "e.g., High Sensitivity, Deep Grounding",
    "crystal": "e.g., Black Tourmaline, Amethyst",
    "chakra": "e.g., Root Chakra, Third Eye"
}`;
          try {
            const rawResponse = await runAIFallback({ prompt, fallbackTemplate: JSON.stringify(defaultSpecialistData) });
            return JSON.parse(rawResponse.replace(/```json/g, '').replace(/```/g, '').trim());
          } catch (err) {
            console.error("Dashboard Specialist AI parsing error:", err);
            return defaultSpecialistData;
          }
        },
        [`dashboard-specialist-${data.dashboard.userId}-${todayStr}`],
        { revalidate: 86400 }
      );

      data.dashboard.specialistStats.alignment = await getCachedSpecialistForecast();
    }

    return NextResponse.json(data);
  } catch (error) {
    console.error('Dashboard Proxy Error:', error);
    return NextResponse.json({ error: 'Failed to connect to backend database' }, { status: 500 });
  }
}