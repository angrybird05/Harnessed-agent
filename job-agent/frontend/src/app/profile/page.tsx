"use client";

import { useEffect, useState } from "react"; // MED-04: removed unused useCallback

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface ProfileData {
  full_name: string;
  phone: string;
  skills: string;
  education: string;
  experience: string;
  projects: string;
  certifications: string;
  github_url: string;
  linkedin_url: string;
  portfolio_url: string;
  preferred_roles: string;
  preferred_locations: string;
  years_of_experience: number;
  resume_summary: string;
}

const emptyProfile: ProfileData = {
  full_name: "",
  phone: "",
  skills: "[]",
  education: "[]",
  experience: "[]",
  projects: "[]",
  certifications: "[]",
  github_url: "",
  linkedin_url: "",
  portfolio_url: "",
  preferred_roles: "[]",
  preferred_locations: "[]",
  years_of_experience: 0,
  resume_summary: "",
};

export default function ProfilePage() {
  const [profile, setProfile] = useState<ProfileData>(emptyProfile);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");

  // Tag input states
  const [skillInput, setSkillInput] = useState("");
  const [roleInput, setRoleInput] = useState("");
  const [locationInput, setLocationInput] = useState("");
  const [certInput, setCertInput] = useState("");

  const parseJsonArray = (s: string): string[] => {
    try {
      const parsed = JSON.parse(s);
      return Array.isArray(parsed) ? parsed : [];
    } catch {
      return [];
    }
  };

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      setLoading(false);
      return;
    }

    fetch(`${API_URL}/profile`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((r) => r.json())
      .then((data) => {
        setProfile({
          full_name: data.full_name || "",
          phone: data.phone || "",
          skills: data.skills || "[]",
          education: data.education || "[]",
          experience: data.experience || "[]",
          projects: data.projects || "[]",
          certifications: data.certifications || "[]",
          github_url: data.github_url || "",
          linkedin_url: data.linkedin_url || "",
          portfolio_url: data.portfolio_url || "",
          preferred_roles: data.preferred_roles || "[]",
          preferred_locations: data.preferred_locations || "[]",
          years_of_experience: data.years_of_experience || 0,
          resume_summary: data.resume_summary || "",
        });
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const handleSave = async () => {
    const token = localStorage.getItem("access_token");
    if (!token) return;

    setSaving(true);
    setMessage("");

    try {
      const res = await fetch(`${API_URL}/profile`, {
        method: "PUT",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(profile),
      });

      if (res.ok) {
        setMessage("Profile saved successfully!");
      } else {
        setMessage("Failed to save profile.");
      }
    } catch (err) {
      setMessage("Error saving profile.");
      console.error(err);
    } finally {
      setSaving(false);
      setTimeout(() => setMessage(""), 3000);
    }
  };

  const addTag = (field: keyof ProfileData, value: string) => {
    if (!value.trim()) return;
    const current = parseJsonArray(profile[field] as string);
    if (!current.includes(value.trim())) {
      current.push(value.trim());
      setProfile({ ...profile, [field]: JSON.stringify(current) });
    }
  };

  const removeTag = (field: keyof ProfileData, index: number) => {
    const current = parseJsonArray(profile[field] as string);
    current.splice(index, 1);
    setProfile({ ...profile, [field]: JSON.stringify(current) });
  };

  const TagInput = ({
    label,
    field,
    inputValue,
    setInputValue,
    placeholder,
  }: {
    label: string;
    field: keyof ProfileData;
    inputValue: string;
    setInputValue: (v: string) => void;
    placeholder: string;
  }) => {
    const tags = parseJsonArray(profile[field] as string);
    return (
      <div>
        <label className="label-text">{label}</label>
        <div className="flex flex-wrap gap-1.5 mb-2">
          {tags.map((tag, i) => (
            <span
              key={i}
              className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-primary-500/10 text-primary-300 text-xs font-medium border border-primary-500/20"
            >
              {tag}
              <button
                onClick={() => removeTag(field, i)}
                className="hover:text-red-400 transition-colors"
              >
                ×
              </button>
            </span>
          ))}
        </div>
        <div className="flex gap-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                e.preventDefault();
                addTag(field, inputValue);
                setInputValue("");
              }
            }}
            placeholder={placeholder}
            className="input-field text-sm flex-1"
          />
          <button
            onClick={() => {
              addTag(field, inputValue);
              setInputValue("");
            }}
            className="btn-secondary text-xs"
          >
            Add
          </button>
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-2 border-primary-400 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-3xl">
      <div>
        <h1 className="text-3xl font-bold bg-gradient-to-r from-white to-surface-200 bg-clip-text text-transparent">
          Profile
        </h1>
        <p className="text-surface-200 mt-1">
          Manage your professional profile for job applications
        </p>
      </div>

      <div className="glass-card p-8 space-y-6">
        {/* Basic Info */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="label-text">Full Name</label>
            <input
              type="text"
              value={profile.full_name}
              onChange={(e) =>
                setProfile({ ...profile, full_name: e.target.value })
              }
              className="input-field"
              placeholder="Jane Developer"
            />
          </div>
          <div>
            <label className="label-text">Phone</label>
            <input
              type="text"
              value={profile.phone}
              onChange={(e) =>
                setProfile({ ...profile, phone: e.target.value })
              }
              className="input-field"
              placeholder="+1-555-0100"
            />
          </div>
        </div>

        {/* URLs */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="label-text">GitHub URL</label>
            <input
              type="url"
              value={profile.github_url}
              onChange={(e) =>
                setProfile({ ...profile, github_url: e.target.value })
              }
              className="input-field text-sm"
              placeholder="https://github.com/..."
            />
          </div>
          <div>
            <label className="label-text">LinkedIn URL</label>
            <input
              type="url"
              value={profile.linkedin_url}
              onChange={(e) =>
                setProfile({ ...profile, linkedin_url: e.target.value })
              }
              className="input-field text-sm"
              placeholder="https://linkedin.com/in/..."
            />
          </div>
          <div>
            <label className="label-text">Portfolio URL</label>
            <input
              type="url"
              value={profile.portfolio_url}
              onChange={(e) =>
                setProfile({ ...profile, portfolio_url: e.target.value })
              }
              className="input-field text-sm"
              placeholder="https://yoursite.com"
            />
          </div>
        </div>

        {/* Years of Experience */}
        <div className="max-w-xs">
          <label className="label-text">Years of Experience</label>
          <input
            type="number"
            min={0}
            value={profile.years_of_experience}
            onChange={(e) =>
              setProfile({
                ...profile,
                years_of_experience: parseInt(e.target.value) || 0,
              })
            }
            className="input-field"
          />
        </div>

        {/* Resume Summary */}
        <div>
          <label className="label-text">Resume Summary</label>
          <textarea
            value={profile.resume_summary}
            onChange={(e) =>
              setProfile({ ...profile, resume_summary: e.target.value })
            }
            rows={3}
            className="input-field resize-none"
            placeholder="Brief professional summary..."
          />
        </div>

        {/* Tag Inputs */}
        <TagInput
          label="Skills"
          field="skills"
          inputValue={skillInput}
          setInputValue={setSkillInput}
          placeholder="e.g. Python, React, AWS..."
        />

        <TagInput
          label="Preferred Roles"
          field="preferred_roles"
          inputValue={roleInput}
          setInputValue={setRoleInput}
          placeholder="e.g. Senior Software Engineer..."
        />

        <TagInput
          label="Preferred Locations"
          field="preferred_locations"
          inputValue={locationInput}
          setInputValue={setLocationInput}
          placeholder="e.g. Remote, San Francisco..."
        />

        <TagInput
          label="Certifications"
          field="certifications"
          inputValue={certInput}
          setInputValue={setCertInput}
          placeholder="e.g. AWS Solutions Architect..."
        />

        {/* Experience (JSON editor) */}
        <div>
          <label className="label-text">Experience (JSON)</label>
          <textarea
            value={profile.experience}
            onChange={(e) =>
              setProfile({ ...profile, experience: e.target.value })
            }
            rows={6}
            className="input-field resize-none font-mono text-xs"
            placeholder='[{"title": "...", "company": "...", "dates": "...", "bullets": ["..."]}]'
          />
        </div>

        {/* Projects (JSON editor) */}
        <div>
          <label className="label-text">Projects (JSON)</label>
          <textarea
            value={profile.projects}
            onChange={(e) =>
              setProfile({ ...profile, projects: e.target.value })
            }
            rows={4}
            className="input-field resize-none font-mono text-xs"
            placeholder='[{"name": "...", "description": "...", "tech": ["..."]}]'
          />
        </div>

        {/* Education (JSON editor) */}
        <div>
          <label className="label-text">Education (JSON)</label>
          <textarea
            value={profile.education}
            onChange={(e) =>
              setProfile({ ...profile, education: e.target.value })
            }
            rows={3}
            className="input-field resize-none font-mono text-xs"
            placeholder='[{"degree": "...", "institution": "...", "year": "..."}]'
          />
        </div>

        {/* Save Button */}
        <div className="flex items-center gap-4 pt-4 border-t border-white/10">
          <button
            onClick={handleSave}
            disabled={saving}
            className="btn-primary disabled:opacity-50"
          >
            {saving ? "Saving..." : "Save Profile"}
          </button>
          {message && (
            <p
              className={`text-sm font-medium ${
                message.includes("success")
                  ? "text-emerald-400"
                  : "text-red-400"
              }`}
            >
              {message}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
