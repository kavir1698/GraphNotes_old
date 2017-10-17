import os

from sqlalchemy import Column, Integer, String, ForeignKey, create_engine, or_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, aliased

from bibtex import *

import datetime
from shutil import copyfile
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
        return "Concept(id={}, name={:.5}, synonyms={:.5}, synonyms={})".format(
            self.id if self.id is not None else 'None', 
            self.name if self.name else 'None', 
            self.synonyms if self.synonyms else 'None', 
            self.subcategories if self.subcategories else 'None')

    def isEmpty(self):
        return not bool(self.name)


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
        return "Subcategory(id={}, subcategory={:.5}, concept_id={}, study={:.5}, description={})".format(
            self.id if self.id is not None else 'None', 
            self.subcategory if self.subcategory else 'None', 
            self.concept_id if self.concept_id else 'None', 
            self.study if self.study else 'None',
            self.description if self.description else '[]')

    def isEmpty(self):
        # todo: add checking description. self.desciption == [] doesn't work
        return not bool(self.subcategory)


class Description(Base):
    __tablename__ = 'descriptions'
    id = Column(Integer, primary_key=True)
    text = Column(String)
    subcategory_id = Column(Integer, ForeignKey("subcategories.id", ondelete="CASCADE"))
    reference = relationship("ConceptReference", cascade='all,delete', backref="node")

    def __repr__(self):
        return "Description(id={}, text={:.5}, subcategory_id={}, references={})".format(
            self.id if self.id is not None else 'None', 
            self.text if self.text else 'None', 
            self.subcategory_id if self.subcategory_id is not None else 'None', 
            self.reference if self.reference else '[]')


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
        return "Description(id={}, description={:.5}, study={:.5}, node1_id={}, node1_id={}, references={})".format(
            self.id if self.id is not None else None, 
            self.description if self.description else 'None', 
            self.study if self.study else 'None',
            self.node1_id if self.node1_id else 'None', 
            self.node2_id if self.node2_id else 'None', 
            self.reference if self.reference else '[]' )

    def isEmpty(self):
        
        return not bool(getPlainText(self.description))


class ConceptReference(Base):
    """
    Class for reference
    """
    __tablename__ = 'concept_references'
    id = Column(Integer, primary_key=True)
    node_id = Column(Integer, ForeignKey('descriptions.id', ondelete="CASCADE"))
    text = Column(String)
    
    def __repr__(self):
        return "ConceptReference(id={}, text={:.5}, node_id={})".format(
            self.id if self.id is not None else 'None', 
            self.text if self.text else 'None', 
            self.node_id if self.node_id is not None else 'None')   

class RelationReference(Base):
    """
    Class for reference
    """
    __tablename__ = 'relation_references'
    id = Column(Integer, primary_key=True)
    relation_id = Column(Integer, ForeignKey('relations.id', ondelete="CASCADE"))
    text = Column(String)

    def __repr__(self):
        return "RelationReference(id={}, text={:.5}, relation_id={})".format(
                self.id if self.id is not None else 'None', 
                self.text if self.text else 'None', 
                self.relation_id if self.relation_id is not None else 'None')   



class Graph:
    """This class is used for communication GUI with the database."""

    def __init__(self, filepath):
        """filepath - path to database"""
        self.filepath = filepath
        self.engine = create_engine(r'sqlite:///{}'.format(filepath))
        if os.path.exists(filepath):
            self.connect_to_database()
        else:
            self.create_database()
            self.connect_to_database(created=True)

    def get_schema_version(self):
        cursor = self.session.execute('PRAGMA user_version')
        return cursor.fetchone()[0]
    
    def set_schema_version(self, version):
        self.session.execute('PRAGMA user_version={}'.format(version))    
        
    def check_schema_version(self, created=False):
        if created:
            self.set_schema_version(1)
            return
        version = self.get_schema_version()
        print("DB VERSION: {}".format(version))
        if version != 0:
            return
        
        try:
            # Copy database
            copyfile(self.filepath, self.filepath + "_old")
        except:
            raise Exception("Can't copy database for migration to new version")
        
        # update all references
        
        # Get all references
        all_concept_references = self.session.query(ConceptReference).all()
        all_relation_references = self.session.query(RelationReference).all()
        # Iterate over concept references 
        for ref in all_concept_references:
            parsed_line = getBibStrFromRender(ref.text)
            
            ref.text = parsed_line
            
            
        # Iterate over relation references 
        for ref in all_relation_references:
            try:
                ref.text = getBibStrFromRender(ref.text)
            except: pass
        
        self.session.commit()
        self.set_schema_version(1)
        
    def __repr__(self):
        return str(self.session)

    def close_connection(self):
        self.session.close()

    def create_database(self):
        Base.metadata.create_all(self.engine)

    def connect_to_database(self, created=False):    
        Base.metadata.bind = self.engine
        self.session = sessionmaker(bind=self.engine)()
        self.check_schema_version(created)
        

    def search_nodes(self, subcategory, selected_items):
        """This method search nodes by the parameter. parameter - Subcategory class"""
        query_list = []
        # aliased needs for an escape of SQL error of two columns with the same name. ID as example
        con = aliased(Concept)
        sub = aliased(Subcategory)
        des = aliased(Description)
        ref = aliased(ConceptReference)
        
        
        query = self.session.query(con, sub)
        query = query.join(sub)
        query = query.outerjoin(des)
        query = query.outerjoin(ref)
        
        if subcategory.subcategory is not None:
            

            subcategory_text = getPlainText(str(subcategory.subcategory))
            subcategory_text = subcategory_text.replace('\n', ' ')
            subcategory_text = subcategory_text.replace('\t', ' ')
            subcategory_text = subcategory_text.replace('.', ' ')
            subcategory_text = subcategory_text.replace(',', ' ')
            subcategory_text = subcategory_text.replace(': ', '')
            query_param = "%{}%".format("%".join(subcategory_text.split()))

            query1_1 = query.filter(sub.subcategory.contains(query_param))
            query1_2 = query.filter(con.synonyms.contains(query_param))
            query1_3 = query.filter(con.name.contains(query_param))
            
            query_list.append(query1_1)
            query_list.append(query1_2)
            query_list.append(query1_3)
           

        if subcategory.description:
            
            if subcategory.description[0].text:
               
                desctiption_text = getPlainText(subcategory.description[0].text)
                query_param = "%{}%".format("%".join(desctiption_text.split()))              
                query2 = query.filter(des.text.contains(query_param))
                query_list.append(query2)
                
                
            if subcategory.description[0].reference:
                
                if subcategory.description[0].reference[0].text:
                    reference_text = getPlainText(str(subcategory.description[0].reference[0].text))
                    reference_text = reference_text.replace('\n', ' ')
                    reference_text = reference_text.replace('\t', ' ')
                    reference_text = reference_text.replace('.', ' ')
                    reference_text = reference_text.replace(',', ' ')
                    reference_text = reference_text.replace(': ', '')
                    query_param = "%{}%".format("%".join(reference_text.split()))
                    query3 = query.filter(ref.text.contains(query_param))
                    query_list.append(query3)                    

        if subcategory.study is not None:
            query4 = query.filter(sub.study.ilike("%{}%".format(subcategory.study)))
            query_list.append(query4)
        
        if selected_items:
            query5 = query.filter(sub.id.in_([s.id for s in selected_items]))
            query_list.append(query5)        
            
        if len(query_list) > 0:
            
            q = query_list[0]
            
            for x in query_list[1:]:
                q = q.union(x)
            result = q.all()
            
            return result
        return []

    def get_all_references(self):
        all_concept_references = self.session.query(ConceptReference).all()
        all_relation_references = self.session.query(RelationReference).all()
        all_concept_references = all_concept_references if isinstance(all_concept_references, list) else [all_concept_references]
        all_relation_references = all_relation_references if isinstance(all_relation_references, list) else [all_relation_references]
        all_concept_references += all_relation_references
        return all_concept_references
        
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
        ref = aliased(reference_class)
        
        query = self.session.query(reference_class.text)
        query = query.group_by(reference_class.text)
        reference_text = str(parametr)
        
        
        
        reference_text = reference_text.replace('\n', ' ')
        reference_text = reference_text.replace('\t', ' ')
        reference_text = reference_text.replace('.', ' ')
        reference_text = reference_text.replace(',', ' ')
        reference_text = reference_text.replace(': ', '')
        query_param = "%{}%".format("%".join(reference_text.split()))
        query = query.filter(ref.text.contains(query_param))
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
