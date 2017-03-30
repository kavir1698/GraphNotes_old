import os
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine, or_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, aliased

Base = declarative_base()


class Concept(Base):
    """
    Class for concepts
    """
    __tablename__ = 'concepts'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    synonyms = Column(String)
    subcategories = relationship("Subcategory", cascade='all,delete', backref="concept")

    def __repr__(self):
        return "{}; {}; {}".format(self.id, self.name, self.synonyms)

    def isEmpty(self):
        return self.name == "" and self.synonyms == ""


class Subcategory(Base):
    """
    Class for subcategory. It's a node in graph
    """
    __tablename__ = 'subcategories'
    id = Column(Integer, primary_key=True)
    subcategory = Column(String)
    concept_id = Column(Integer, ForeignKey('concepts.id', ondelete="CASCADE"))
    description = relationship("Description", cascade='all,delete', backref='subcategory')
    study = Column(String)
    relation1 = relationship("Relation", foreign_keys="[Relation.node1_id]", cascade='delete-orphan,all',
                             backref="node1")
    relation2 = relationship("Relation", foreign_keys="[Relation.node2_id]", cascade='delete-orphan,all',
                             backref="node2")

    def __repr__(self):
        return "{}; {}; {};".format(self.id, self.subcategory, self.description)

    def isEmpty(self):
        # todo: add checking description. self.desciption == [] doesn't work
        return self.subcategory == "" and self.study == ""


class Description(Base):
    __tablename__ = 'descriptions'
    id = Column(Integer, primary_key=True)
    text = Column(String)
    subcategory_id = Column(Integer, ForeignKey("subcategories.id", ondelete="CASCADE"))
    reference = relationship("ConceptReference", cascade='all,delete', backref="node")

    def __repr__(self):
        return "{}, {}, {}".format(self.id, self.text, self.subcategory_id)


class Relation(Base):
    """
    Class for relation between two concepts. It's a edge in graph
    """
    __tablename__ = "relations"
    id = Column(Integer, primary_key=True)
    node1_id = Column(Integer, ForeignKey('subcategories.id'))
    node2_id = Column(Integer, ForeignKey('subcategories.id'))
    description = Column(String)
    study = Column(String)
    # node1 = relationship(Subcategory, foreign_keys=[node1_id], cascade='delete,all')
    # node2 = relationship(Subcategory, foreign_keys=[node2_id], cascade='delete,all')
    reference = relationship("RelationReference", cascade='delete,all', backref="relation")

    def __repr__(self):
        return "{}; {}; {}; {}; {}; {};".format(self.id, self.description, self.study,
                                                self.node1_id, self.node2_id, self.reference, )

    def isEmpty(self):
        return self.description == ""


class ConceptReference(Base):
    """
    Class for reference
    """
    __tablename__ = 'concept_references'
    id = Column(Integer, primary_key=True)
    node_id = Column(Integer, ForeignKey('descriptions.id', ondelete="CASCADE"))
    text = Column(String)


class RelationReference(Base):
    """
    Class for reference
    """
    __tablename__ = 'relation_references'
    id = Column(Integer, primary_key=True)
    relation_id = Column(Integer, ForeignKey('relations.id', ondelete="CASCADE"))
    text = Column(String)

    def __repr__(self):
        return self.text


class Graph:
    """This class is used for communication GUI with the database."""

    def __init__(self, filepath):
        """filepath - path to database"""
        self.engine = create_engine(r'sqlite:///{}'.format(filepath))
        if os.path.exists(filepath):
            self.connect_to_database()
        else:
            self.create_database()
            self.connect_to_database()

    def __repr__(self):
        return str(self.session)

    def close_connection(self):
        self.session.close()

    def create_database(self):
        Base.metadata.create_all(self.engine)

    def connect_to_database(self):
        Base.metadata.bind = self.engine
        self.session = sessionmaker(bind=self.engine)()

    def search_nodes(self, subcategory):
        """This method search nodes by the parameter. parameter - Subcategory class"""
        query_list = []
        # aliased needs for an escape of SQL error of two columns with the same name. ID as example
        con = aliased(Concept)
        sub = aliased(Subcategory)
        des = aliased(Description)
        query = self.session.query(con, sub)
        query = query.join(sub)
        query = query.outerjoin(des)
        if subcategory.subcategory is not None:
            query1 = query.filter(
                or_(
                    (con.name + " " + sub.subcategory).ilike("%{}%".format(subcategory.subcategory)),
                    (sub.subcategory + " " + Concept.name).ilike("%{}%".format(subcategory.subcategory)),
                    sub.subcategory.ilike("%{}%".format(subcategory.subcategory)),
                    con.name.ilike("%{}%".format(subcategory.subcategory)),
                    con.synonyms.ilike("%{}%".format(subcategory.subcategory))
                )
            )
            query_list.append(query1)

        if subcategory.description:
            query2 = query.filter(des.text.ilike("%{}%".format(subcategory.description[0].text)))
            query_list.append(query2)

        if subcategory.study is not None:
            query3 = query.filter(sub.study.ilike("%{}%".format(subcategory.study)))
            query_list.append(query3)

        if len(query_list) > 0:
            q = query_list[0]
            [q.union(x) for x in query_list[1:]]
            result = q.all()
            result = [n for n in result]
            return result
        return []

    def get_similar(self, something):
        """This method searches in database very similar object to "something" and returns this.
        If no similar in the database this method returns "something" without changes.

        something - Concept or Subcategory object
        """

        if isinstance(something, Concept):
            query = self.session.query(Concept)
            query = query.filter(Concept.name.ilike(something.name))
            result = query.first()
            return something if result is None else result
        elif isinstance(something, Subcategory):
            query = self.session.query(Concept, Subcategory)
            query = query.join(Concept.subcategories)
            query = query.filter(Subcategory.subcategory.ilike(something.subcategory))
            concept = self.session.query(Concept).get(something.concept_id)
            query = query.filter(Concept.name.like(concept.name))
            result = query.first()
            if result is None:
                return something
            else:
                subcategory = result[1]
                if something.description:
                    subcategory.description += something.description
                return subcategory
        else:
            raise type(something)

    def search_references(self, parametr, reference_class):
        """This method searches references in the database
        and returns a list of the reference object.
        Because database has two different type of reference,
        there is reference class as a parameter of the function.

        parameter - RelationRefence or ConceptReference object
        reference_class - RelationReference or ConceptReference class
        """
        query = self.session.query(reference_class.text)
        query = query.group_by(reference_class.text)
        query = query.filter(reference_class.text.ilike("%{}%".format(parametr)))
        return query.all()

    def add_and_flush(self, something):
        self.session.add(something)
        self.session.flush()

    def search_relation(self, subcategory_id):
        """This method search all relation with a concept that represents as ID of the subcategory.
        subcategory_id = ID of subcategory
        """
        subcategory1 = aliased(Subcategory)
        subcategory2 = aliased(Subcategory)
        concept1 = aliased(Concept)
        concept2 = aliased(Concept)

        query1 = self.session.query(concept2, subcategory2, Relation)
        query1 = query1.join(subcategory1, Relation.node1)
        query1 = query1.join(subcategory2, Relation.node2)
        query1 = query1.join(concept1, subcategory1.concept)
        query1 = query1.join(concept2, subcategory2.concept)

        query2 = self.session.query(concept1, subcategory1, Relation)
        query2 = query2.join(subcategory1, Relation.node1)
        query2 = query2.join(subcategory2, Relation.node2)
        query2 = query2.join(concept1, subcategory1.concept)
        query2 = query2.join(concept2, subcategory2.concept)

        query1 = query1.filter(subcategory1.id == subcategory_id)
        query2 = query2.filter(subcategory2.id == subcategory_id)
        query = query1.union(query2)
        result = query.all()
        return result

    def delete(self, something):
        self.session.delete(something)
        self.session.commit()

    def update_concept(self, concept):
        c = self.session.query(Concept).get(concept.id)
        c.name = concept.name
        c.synonyms = concept.synonyms
        self.session.commit()

    def update_reference(self, reference):
        if isinstance(reference, ConceptReference):
            r = self.session.query(ConceptReference).get(reference.id)
        else:
            r = self.session.query(RelationReference).get(reference.id)
        r.text = reference.text
        self.session.commit()

    def update_description(self, description):
        if description.id is None:
            self.add_and_flush(description)
        r = self.session.query(Description).get(description.id)
        r.text = description.text
        self.session.commit()

    def update_relation(self, relation):
        c = self.session.query(Relation).get(relation.id)
        c.description = relation.description
        c.study = relation.study
        self.session.commit()

    def update_subcategory(self, subcategory):
        s = self.session.query(Subcategory).get(subcategory.id)
        s.subcategory = subcategory.subcategory
        s.study = subcategory.study
        self.session.commit()

    def commit(self, something=None):
        if something:
            self.session.add(something)
        self.session.commit()
