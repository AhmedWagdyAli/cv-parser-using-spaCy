from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class CV(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_title = db.Column(db.String(255), nullable=True)
    years_of_experience = db.Column(db.Integer, nullable=True)
    path_of_cv = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(255), nullable=True)
    email = db.Column(db.String(255), nullable=True)
    certificates = db.relationship(
        "Certificates", backref="cv", cascade="all, delete-orphan", lazy="dynamic"
    )
    skills = db.relationship(
        "Skills", backref="cv", cascade="all, delete-orphan", lazy="dynamic"
    )
    experiences = db.relationship(
        "Experiences", backref="cv", cascade="all, delete-orphan", lazy="dynamic"
    )

    def __repr__(self):
        return f"<CV id={self.id}, job_title={self.job_title}, path_of_cv={self.path_of_cv}>"


class Certificates(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cv_id = db.Column(
        db.Integer, db.ForeignKey("cv.id", ondelete="CASCADE"), nullable=False
    )
    name = db.Column(db.String(255), nullable=False)


class Skills(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cv_id = db.Column(
        db.Integer, db.ForeignKey("cv.id", ondelete="CASCADE"), nullable=False
    )
    name = db.Column(db.String(255), nullable=False)


class Experiences(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cv_id = db.Column(
        db.Integer, db.ForeignKey("cv.id", ondelete="CASCADE"), nullable=False
    )
    company = db.Column(db.String(255), nullable=True)
    role = db.Column(db.String(255), nullable=True)
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    description = db.Column(db.String(255), nullable=True)
