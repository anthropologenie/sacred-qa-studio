@router.get("/sankalpa")
async def list_sankalpa(limit: int = 10, db: Session = Depends(get_db)):
    return db.query(Sankalpa).order_by(Sankalpa.created_at.desc()).limit(limit).all()

@router.get("/sankalpa/{id}")
async def get_sankalpa(id: UUID, db: Session = Depends(get_db)):
    sankalpa = db.query(Sankalpa).filter(Sankalpa.id == id).first()
    if not sankalpa:
        raise HTTPException(status_code=404, detail="Not found")
    return sankalpa

@router.patch("/sankalpa/{id}")
async def update_sankalpa(id: UUID, status: str, db: Session = Depends(get_db)):
    sankalpa = db.query(Sankalpa).filter(Sankalpa.id == id).first()
    if not sankalpa:
        raise HTTPException(status_code=404, detail="Not found")
    sankalpa.status = status
    if status == "completed":
        sankalpa.completed_at = func.now()
    db.commit()
    return sankalpa
