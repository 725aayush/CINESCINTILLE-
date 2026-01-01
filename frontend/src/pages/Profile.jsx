import { useEffect, useState } from "react";
import api from "../api";
import Header from "../components/Header";
import Footer from "../components/Footer";
import MovieRow from "../components/MovieRow";
import "../styles/profile.css";

export default function Profile() {
  const [user, setUser] = useState(null);
  const [watchlist, setWatchlist] = useState([]);
  const [watched, setWatched] = useState([]);
  const [reviews, setReviews] = useState([]);

  // Edit states
  const [isEditing, setIsEditing] = useState(false);
  const [name, setName] = useState("");
  const [age, setAge] = useState("");
  const [selectedAvatar, setSelectedAvatar] = useState("");

  // Your specific avatar list
  const avatarOptions = [
    "avatar1.png", "avatar2.png", "avatar3.png", 
    "avatar4.png", "avatar5.png", "default.jpg"
  ];

  useEffect(() => {
    api.get("/profile").then(res => {
      setUser(res.data);
      setName(res.data.name || "");
      setAge(res.data.age || "");
      setSelectedAvatar(res.data.avatar || "default.jpg");
    }).catch(err => console.error("Profile fetch error", err));

    api.get("/profile/watchlist").then(res => setWatchlist(res.data));
    api.get("/profile/watched").then(res => setWatched(res.data));
    api.get("/profile/reviews").then(res => setReviews(res.data));
  }, []);

  const saveProfile = async () => {
    try {
      await api.post("/profile/update", { name, age, avatar: selectedAvatar });
      setUser({ ...user, name, age, avatar: selectedAvatar });
      setIsEditing(false);
      alert("Profile updated successfully!");
    } catch (err) {
      alert("Failed to update profile.");
    }
  };

  if (!user) return <div className="loading">Loading Profile...</div>;

  return (
    <div className="profile-container">
      <Header />

      <div className="profile-page">
        <div className="profile-header">
          <div className="avatar-wrapper">
            <img
              src={`/static/avatars/${isEditing ? selectedAvatar : user.avatar}`}
              className="profile-avatar-main"
              alt="User Avatar"
            />
            {isEditing && (
              <div className="avatar-selector">
                <p>Choose Avatar:</p>
                <div className="avatar-grid">
                  {avatarOptions.map((av) => (
                    <img
                      key={av}
                      src={`/static/avatars/${av}`}
                      className={`avatar-option ${selectedAvatar === av ? "active" : ""}`}
                      onClick={() => setSelectedAvatar(av)}
                      alt="option"
                    />
                  ))}
                </div>
              </div>
            )}
          </div>

          <div className="profile-info-block">
            {isEditing ? (
              <div className="edit-fields">
                <div className="input-group">
                  <label>Full Name</label>
                  <input value={name} onChange={e => setName(e.target.value)} placeholder="Enter Name" />
                </div>
                <div className="input-group">
                  <label>Age</label>
                  <input type="number" value={age} onChange={e => setAge(e.target.value)} placeholder="Age" />
                </div>
                <div className="button-group">
                  <button className="save-btn" onClick={saveProfile}>Save Changes</button>
                  <button className="cancel-btn" onClick={() => setIsEditing(false)}>Cancel</button>
                </div>
              </div>
            ) : (
              <div className="display-fields">
                <h1>{user.name || user.username}</h1>
                <p className="username-tag">@{user.username}</p>
                <p className="email-tag">{user.email}</p>
                {user.age && <p className="age-tag">Age: {user.age}</p>}
                <button className="edit-toggle-btn" onClick={() => setIsEditing(true)}>Edit Profile</button>
              </div>
            )}
          </div>
        </div>

        <div className="profile-content">
          <MovieRow title="📌 Your Watchlist" movies={watchlist} />
          <MovieRow title="✔ Movies Watched" movies={watched} />

          <div className="user-reviews-section">
            <h3>Your Recent Reviews</h3>
            {reviews.length === 0 ? (
              <p className="empty-msg">No reviews yet.</p>
            ) : (
              <div className="reviews-grid">
                {reviews.map((r, i) => (
                  <div key={i} className="profile-review-card">
                    <h4>{r.movie_title}</h4>
                    <div className="rating-stars">{"★".repeat(r.rating)}</div>
                    <p>{r.comment || "No comment provided."}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      <Footer />
    </div>
  );
}