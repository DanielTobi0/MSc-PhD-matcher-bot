import Link from "next/link";

export const metadata = { title: "Privacy - MSc PhD Matcher" };

export default function PrivacyPage() {
  return (
    <main className="mx-auto max-w-2xl px-5 py-12 text-lg leading-relaxed">
      <h1 className="mb-6 text-3xl font-bold">Privacy</h1>
      <p className="mb-4">This is a free, community-run tool. It is not a company and has no staff. Here is what it keeps and why.</p>
      <h2 className="mb-2 mt-6 text-xl font-bold">What we store</h2>
      <ul className="mb-4 list-disc pl-6">
        <li>Your email and a password hash (Supabase Auth).</li>
        <li>Your preferences, saved openings and notes.</li>
        <li>Your CV file and the text extracted from it, if you upload one.</li>
        <li>Your AI provider key, encrypted and bound to your account. It is never shown back to you or to the browser.</li>
      </ul>
      <h2 className="mb-2 mt-6 text-xl font-bold">Who sees it</h2>
      <p className="mb-4">
        Only you, and the site owner in a technical sense (database access). Your CV text is sent to the AI provider you chose, using your own key,
        to read it and score openings. That provider&apos;s privacy terms apply to that data. We do not sell data or show ads.
      </p>
      <h2 className="mb-2 mt-6 text-xl font-bold">Deleting your data</h2>
      <p className="mb-4">
        In <Link href="/settings/" className="font-bold text-brand underline">Settings</Link> use &quot;Delete my account&quot;. It removes your CV file,
        extracted text, matches, notes, stored key and login immediately. You can also remove just your AI key or replace your CV there.
      </p>
      <h2 className="mb-2 mt-6 text-xl font-bold">Contact</h2>
      <p>Report security problems through the repository&apos;s Security tab (see SECURITY.md).</p>
    </main>
  );
}
