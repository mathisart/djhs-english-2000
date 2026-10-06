import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const cors = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods": "POST, OPTIONS"
};

const XP: Record<string, number> = {
  correct: 2,
  review: 4,
  listening: 4,
  context: 5,
  mastered: 25
};

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: cors });
  if (req.method !== "POST") return new Response("Method not allowed", { status: 405, headers: cors });

  try {
    const body = await req.json();
    const action = String(body.action || "");
    const token = String(body.deviceToken || "");
    const nickname = String(body.nickname || "").trim().slice(0, 20);
    const word = String(body.word || "").trim().slice(0, 80);
    const eventType = String(body.eventType || "");

    if (!/^[0-9a-f-]{36}$/i.test(token)) throw new Error("Invalid device token");

    const admin = createClient(
      Deno.env.get("SUPABASE_URL")!,
      Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!
    );

    if (action === "register") {
      if (!nickname || nickname.length > 20) throw new Error("Invalid nickname");
      const { data: existing } = await admin.from("players").select("id,nickname,xp,weekly_xp,mastered_words,best_combo").eq("device_token", token).maybeSingle();
      if (existing) {
        const { data, error } = await admin.from("players").update({ nickname }).eq("id", existing.id).select("id,nickname,xp,weekly_xp,mastered_words,best_combo").single();
        if (error) throw error;
        return Response.json(data, { headers: cors });
      }
      const { data, error } = await admin.from("players").insert({ device_token: token, nickname }).select("id,nickname,xp,weekly_xp,mastered_words,best_combo").single();
      if (error) throw error;
      return Response.json(data, { headers: cors });
    }

    if (action === "event") {
      if (!word || !(eventType in XP)) throw new Error("Invalid learning event");
      const { data: player, error: pe } = await admin.from("players").select("id,xp,weekly_xp,mastered_words,best_combo").eq("device_token", token).single();
      if (pe) throw pe;

      // Server chooses XP; the browser never submits an XP amount.
      let gain = XP[eventType];
      const since = new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString();
      const { count } = await admin.from("learning_events").select("id", { count: "exact", head: true }).eq("player_id", player.id).eq("word", word).eq("event_type", eventType).gte("created_at", since);
      if ((count || 0) >= 3) gain = 0;

      const mastered = eventType === "mastered" ? player.mastered_words + 1 : player.mastered_words;
      const bestCombo = Math.max(player.best_combo, Math.max(0, Math.min(999, Number(body.combo) || 0)));
      if (gain > 0) {
        const { error: ee } = await admin.from("learning_events").insert({ player_id: player.id, event_type: eventType, word, xp: gain });
        if (ee) throw ee;
      }
      const { data, error } = await admin.from("players").update({
        xp: player.xp + gain,
        weekly_xp: player.weekly_xp + gain,
        mastered_words: mastered,
        best_combo: bestCombo
      }).eq("id", player.id).select("id,nickname,xp,weekly_xp,mastered_words,best_combo").single();
      if (error) throw error;
      return Response.json({ ...data, gained: gain }, { headers: cors });
    }

    throw new Error("Unknown action");
  } catch (e) {
    return Response.json({ error: e instanceof Error ? e.message : "Request failed" }, { status: 400, headers: cors });
  }
});
