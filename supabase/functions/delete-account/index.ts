// Supabase Edge Function: permanently delete the caller's account and data.
// Removes their CV files from Storage, then the auth user; every user table
// cascades on auth.users (profile, CV rows, matches, notes, stored AI key).

import { createClient } from "jsr:@supabase/supabase-js@2";

import { corsHeaders, handleCors } from "../_shared/cors.ts";
import { allowed, TOO_MANY } from "../_shared/ratelimit.ts";

const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const SERVICE_ROLE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
const ANON_KEY = Deno.env.get("SUPABASE_ANON_KEY")!;

const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { ...corsHeaders, "Content-Type": "application/json" } });

Deno.serve(async (req) => {
  const corsResponse = handleCors(req);
  if (corsResponse) return corsResponse;
  if (req.method !== "POST") return json({ error: "Method not allowed" }, 405);

  const authHeader = req.headers.get("Authorization");
  if (!authHeader) return json({ error: "Missing Authorization header" }, 401);

  const callerClient = createClient(SUPABASE_URL, ANON_KEY, { global: { headers: { Authorization: authHeader } } });
  const { data: userData, error: userErr } = await callerClient.auth.getUser();
  if (userErr || !userData?.user) return json({ error: "Invalid session" }, 401);
  const userId = userData.user.id;

  const body = await req.json().catch(() => ({}));
  if (body.confirm !== "DELETE") return json({ error: "Confirmation missing." }, 400);
  if (!(await allowed(userId, "delete-account", 3, "1 hour"))) return json(TOO_MANY, 429);

  const admin = createClient(SUPABASE_URL, SERVICE_ROLE_KEY);

  const { data: files } = await admin.storage.from("cvs").list(userId, { limit: 1000 });
  if (files?.length) {
    const { error: rmErr } = await admin.storage.from("cvs").remove(files.map((f) => `${userId}/${f.name}`));
    if (rmErr) {
      console.error("delete-account: storage removal failed");
      return json({ error: "Could not delete your files. Try again." }, 500);
    }
  }

  const { error: delErr } = await admin.auth.admin.deleteUser(userId);
  if (delErr) {
    console.error("delete-account: user deletion failed");
    return json({ error: "Could not delete your account. Try again." }, 500);
  }
  return json({ ok: true });
});
